"""
Minimal MCP server demonstrating the three primitives: resources, tools, and prompts.

This server exposes:
  - 2 resources: company policies (static text) and recent orders (dynamic JSON)
  - 1 tool: lookup_order_status(order_id)

Run it with:
    python server.py

Consume it from any MCP-compatible client (Claude Desktop, Cursor, Continue, etc.)
by pointing the client at this process via stdio.

Reference: https://modelcontextprotocol.io/
"""
import json
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP


# Initialize the server with a descriptive name that clients will display.
mcp = FastMCP("field-notes-sample-mcp-server")


# A static, versioned knowledge resource the client can load into context.
COMPANY_POLICIES = """
Shipping Policy (v2.3, effective 2026-01-15):
- Orders placed before 14:00 BRT ship the same business day.
- International orders use DHL Express with tracking.
- Refunds are processed within 5 business days of return receipt.

Return Policy (v1.8, effective 2025-11-01):
- 30-day return window from delivery date.
- Items must be unopened and in original packaging.
- Electronics have a 14-day return window.
"""


# A simulated dynamic data source. In a real deployment this would read from
# DynamoDB, RDS, an internal API, whatever. MCP does not care where the data lives.
FAKE_ORDERS = {
    "ORD-1001": {"status": "delivered", "placed_at": "2026-04-20", "customer": "acme-corp"},
    "ORD-1002": {"status": "in_transit", "placed_at": "2026-04-22", "customer": "beta-ltd"},
    "ORD-1003": {"status": "processing", "placed_at": "2026-04-23", "customer": "gamma-sa"},
    "ORD-1004": {"status": "delivered", "placed_at": "2026-04-21", "customer": "acme-corp"},
}


@mcp.resource("policies://company")
def get_policies() -> str:
    """Return the company shipping and return policies."""
    return COMPANY_POLICIES


@mcp.resource("orders://recent")
def get_recent_orders() -> str:
    """Return orders placed in the last 7 days as JSON."""
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent = {
        order_id: data
        for order_id, data in FAKE_ORDERS.items()
        if data["placed_at"] >= cutoff
    }
    return json.dumps(recent, indent=2)


@mcp.tool()
def lookup_order_status(order_id: str) -> str:
    """
    Look up the status of a specific order by its ID.

    Args:
        order_id: Order identifier (e.g., 'ORD-1001').

    Returns:
        Human-readable status message.
    """
    order = FAKE_ORDERS.get(order_id)
    if order is None:
        return f"No order found with ID '{order_id}'."

    return (
        f"Order {order_id} for customer '{order['customer']}' "
        f"was placed on {order['placed_at']} and is currently: {order['status']}."
    )


if __name__ == "__main__":
    # The FastMCP helper handles stdio transport by default, which is what
    # Claude Desktop, Cursor, and most MCP clients expect.
    mcp.run()
