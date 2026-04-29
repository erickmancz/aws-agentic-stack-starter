"""
MCP Server hospedado em AWS Lambda Function URL.

Implementa manualmente o protocolo MCP (JSON-RPC 2.0 sobre HTTP) — sem usar
biblioteca pré-pronta — para que a audiência da apresentação consiga ver
exatamente como o protocolo funciona "por baixo".

Métodos suportados:
  - initialize             handshake inicial com o cliente
  - notifications/initialized  notificação one-way (sem resposta)
  - tools/list             retorna o schema das tools disponíveis
  - tools/call             invoca uma tool e retorna o resultado
  - ping                   health check

Transporte: streamable HTTP em modo stateless. Cada request é independente,
sem session ID. Compatível com qualquer cliente MCP que fale streamable HTTP
(Strands MCPClient, MCP Inspector, Claude Desktop com URL transport, etc).

Reference: https://modelcontextprotocol.io/specification
"""
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ============================================================================
# DOMAIN DATA
# Equivalente ao mcp-server-sample local original, mas dentro do Lambda.
# ============================================================================

COMPANY_POLICIES = (
    "Shipping Policy (v2.3, effective 2026-01-15):\n"
    "- Orders placed before 14:00 BRT ship the same business day.\n"
    "- International orders use DHL Express with tracking.\n"
    "- Refunds are processed within 5 business days of return receipt.\n"
    "\n"
    "Return Policy (v1.8, effective 2025-11-01):\n"
    "- 30-day return window from delivery date.\n"
    "- Items must be unopened and in original packaging.\n"
    "- Electronics have a 14-day return window."
)

FAKE_ORDERS = {
    "ORD-1001": {"status": "delivered",  "placed_at": "2026-04-20", "customer": "acme-corp"},
    "ORD-1002": {"status": "in_transit", "placed_at": "2026-04-22", "customer": "beta-ltd"},
    "ORD-1003": {"status": "processing", "placed_at": "2026-04-23", "customer": "gamma-sa"},
    "ORD-1004": {"status": "delivered",  "placed_at": "2026-04-21", "customer": "acme-corp"},
}


# ============================================================================
# TOOL CATALOG
# Schema retornado em tools/list. Segue JSON Schema draft 2020-12.
# ============================================================================

TOOLS = [
    {
        "name": "lookup_order_status",
        "description": "Look up the status of a specific order by its ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order identifier, e.g., 'ORD-1001'.",
                }
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "get_company_policies",
        "description": (
            "Return the company shipping and return policies. Use this when the "
            "user asks about delivery, returns, or refund rules."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
]


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

def tool_lookup_order_status(arguments: dict) -> str:
    order_id = arguments.get("order_id", "")
    order = FAKE_ORDERS.get(order_id)
    if order is None:
        return f"No order found with ID '{order_id}'."
    return (
        f"Order {order_id} for customer '{order['customer']}' "
        f"was placed on {order['placed_at']} and is currently: {order['status']}."
    )


def tool_get_company_policies(arguments: dict) -> str:
    return COMPANY_POLICIES


TOOL_DISPATCH = {
    "lookup_order_status": tool_lookup_order_status,
    "get_company_policies": tool_get_company_policies,
}


# ============================================================================
# JSON-RPC 2.0 HELPERS
# ============================================================================

def jsonrpc_result(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def jsonrpc_error(request_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


# ============================================================================
# MCP METHOD HANDLERS
# ============================================================================

def handle_initialize(request_id, params):
    """Handshake inicial. Retorna versão do protocolo e capabilities do server."""
    return jsonrpc_result(request_id, {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {
            "name": "field-notes-lambda-mcp",
            "version": "1.0.0",
        },
    })


def handle_tools_list(request_id, params):
    """Retorna o catálogo de tools disponíveis."""
    return jsonrpc_result(request_id, {"tools": TOOLS})


def handle_tools_call(request_id, params):
    """Invoca uma tool e retorna o resultado em formato MCP content."""
    tool_name = params.get("name")
    arguments = params.get("arguments", {}) or {}

    impl = TOOL_DISPATCH.get(tool_name)
    if impl is None:
        return jsonrpc_error(request_id, -32602, f"Unknown tool: {tool_name}")

    try:
        text = impl(arguments)
    except Exception as exc:
        logger.exception("Tool %s raised", tool_name)
        return jsonrpc_error(request_id, -32603, f"Tool execution error: {exc}")

    return jsonrpc_result(request_id, {
        "content": [{"type": "text", "text": text}],
        "isError": False,
    })


def handle_ping(request_id, params):
    return jsonrpc_result(request_id, {})


METHOD_DISPATCH = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
    "ping": handle_ping,
}


# ============================================================================
# LAMBDA HANDLER
# Recebe eventos do Lambda Function URL (formato HTTP API v2).
# ============================================================================

def lambda_handler(event, context):
    logger.info("Received event with method=%s", event.get("requestContext", {}).get("http", {}).get("method"))

    # Health check via GET — útil pra confirmar que o Function URL está vivo.
    http_method = event.get("requestContext", {}).get("http", {}).get("method", "POST")
    if http_method == "GET":
        return _http_response(200, {"status": "ok", "server": "field-notes-lambda-mcp"})

    # Body do request (Function URL entrega como string JSON).
    raw_body = event.get("body", "{}") or "{}"
    if event.get("isBase64Encoded", False):
        import base64
        raw_body = base64.b64decode(raw_body).decode("utf-8")

    try:
        message = json.loads(raw_body)
    except json.JSONDecodeError:
        return _http_response(400, {"error": "Invalid JSON"})

    # Notification (sem id) — protocolo MCP retorna 202 Accepted sem body.
    if "id" not in message and message.get("method", "").startswith("notifications/"):
        logger.info("Received notification: %s", message.get("method"))
        return {"statusCode": 202, "body": ""}

    # Request normal — dispatch pelo método.
    request_id = message.get("id")
    method = message.get("method", "")
    params = message.get("params", {}) or {}

    handler = METHOD_DISPATCH.get(method)
    if handler is None:
        response = jsonrpc_error(request_id, -32601, f"Method not found: {method}")
    else:
        response = handler(request_id, params)

    return _http_response(200, response)


def _http_response(status_code: int, body: dict) -> dict:
    """Envelope HTTP esperado pelo Function URL."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }
