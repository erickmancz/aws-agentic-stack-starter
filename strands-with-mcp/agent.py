"""
Strands agent que consome um MCP server hospedado em AWS Lambda.

Roda em qualquer ambiente Python 3.10+ — recomendado rodar dentro do
AWS CloudShell durante a apresentação para a audiência ver tudo
acontecendo dentro da conta AWS.

Pega a URL do MCP server da variável de ambiente MCP_SERVER_URL.

Reference: https://strandsagents.com/
"""
import os

from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client


# A URL é injetada pelo deploy do SAM. No CloudShell:
#   export MCP_SERVER_URL=$(aws cloudformation describe-stacks \
#     --stack-name field-notes-mcp-demo \
#     --query "Stacks[0].Outputs[?OutputKey=='McpServerUrl'].OutputValue" \
#     --output text)
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "").strip()
if not MCP_SERVER_URL:
    raise SystemExit(
        "Defina MCP_SERVER_URL antes de rodar.\n"
        "  export MCP_SERVER_URL=https://...lambda-url.us-east-1.on.aws/"
    )


def build_mcp_client() -> MCPClient:
    """
    Cria um cliente MCP que conecta ao Lambda via streamable HTTP.

    O `streamablehttp_client` é a implementação oficial do MCP SDK Python
    para o transporte HTTP. Ele faz POST com JSON-RPC e parseia a resposta.
    """
    return MCPClient(lambda: streamablehttp_client(MCP_SERVER_URL))


def main():
    print(f"--- Connecting to MCP server at {MCP_SERVER_URL} ---")
    mcp_client = build_mcp_client()

    # O bloco `with` garante que o cliente faz initialize/close corretos.
    with mcp_client:
        # Lista as tools que o servidor expõe.
        tools = mcp_client.list_tools_sync()
        print(f"--- Server exposes {len(tools)} tool(s):")
        for t in tools:
            print(f"    · {t.tool_name}")

        # Constrói o agente Strands com Bedrock como modelo provider
        # e as tools do MCP server como ferramentas disponíveis.
        agent = Agent(
            model=BedrockModel(
                # Haiku 4.5 — modelo mais barato disponível e suficiente para
                # tool use simples como o desta demo.
                model_id="anthropic.claude-haiku-4-5-20251001-v1:0",
                region_name="us-east-1",
            ),
            tools=tools,
            system_prompt=(
                "You are a customer support assistant. "
                "Use the available tools to answer questions about orders "
                "and company policies. Be concise."
            ),
        )

        # Pergunta de teste — o modelo decide chamar lookup_order_status.
        question = "What is the status of order ORD-1002?"
        print(f"\n--- User question: {question}")
        response = agent(question)
        print(f"\n--- Agent response ---")
        print(response)


if __name__ == "__main__":
    main()
