# Strands agent + MCP Lambda

Agente Strands rodando no AWS CloudShell, consumindo um MCP server hospedado em AWS Lambda.

## Arquitetura

```
┌────────────────────────────┐
│ AWS CloudShell             │
│ (terminal AWS-native)      │
│                            │
│  ┌──────────────────────┐  │
│  │ agent.py             │  │     POST JSON-RPC 2.0
│  │ ├─ Strands Agent     │──┼────────────────────────────┐
│  │ ├─ MCPClient         │  │     streamable HTTP         │
│  │ └─ BedrockModel      │  │                             ▼
│  └──────────────────────┘  │              ┌──────────────────────────┐
│                            │              │ Lambda Function URL      │
└────────────┬───────────────┘              │ (mcp-lambda module)      │
             │                              │                          │
             │ Bedrock                      │  ┌────────────────────┐  │
             │ InvokeModel                  │  │ handler.py         │  │
             │                              │  │ ├─ tools/list      │  │
             ▼                              │  │ ├─ tools/call      │  │
┌────────────────────────────┐              │  │ └─ initialize      │  │
│ Amazon Bedrock             │              │  └────────────────────┘  │
│ Claude Haiku 4.5           │              └──────────────────────────┘
└────────────────────────────┘
```

## Pré-requisitos

1. **Módulo `mcp-lambda` deployado** — siga `mcp-lambda/README.md` primeiro
2. **Acesso ao modelo Claude Haiku 4.5 habilitado em Bedrock us-east-1**
3. **CloudShell ou outro ambiente Python 3.10+ com credenciais AWS**

## Setup no CloudShell

```bash
# Já dentro do repo no CloudShell
cd aws-agentic-stack-starter/strands-with-mcp

# Cria venv (CloudShell tem 1GB persistente — venv sobrevive entre sessões)
python3.11 -m venv .venv
source .venv/bin/activate

# Instala dependências
pip install -r requirements.txt

# Captura a URL do MCP server deployado
export MCP_SERVER_URL=$(aws cloudformation describe-stacks \
  --stack-name field-notes-mcp-demo \
  --query "Stacks[0].Outputs[?OutputKey=='McpServerUrl'].OutputValue" \
  --output text)

echo "MCP at: $MCP_SERVER_URL"

# Roda o agente
python agent.py
```

Saída esperada:

```
--- Connecting to MCP server at https://abc123.lambda-url.us-east-1.on.aws/ ---
--- Server exposes 2 tool(s):
    · lookup_order_status
    · get_company_policies

--- User question: What is the status of order ORD-1002?

--- Agent response ---
Order ORD-1002 for customer 'beta-ltd' was placed on 2026-04-22 and is currently:
in_transit.
```

## O que está acontecendo por baixo

1. `agent.py` chama `MCPClient.list_tools_sync()` — isso dispara um `initialize` + `tools/list` pro Lambda
2. Lambda responde com o catálogo: `lookup_order_status` e `get_company_policies`
3. Strands monta o agente com essas tools como se fossem nativas
4. Pergunta enviada ao Bedrock — Claude decide chamar `lookup_order_status` com `order_id="ORD-1002"`
5. Strands invoca o MCPClient → POST JSON-RPC `tools/call` no Lambda
6. Lambda executa a função, retorna o resultado
7. Claude usa o resultado para formular a resposta final
8. Você vê tudo no terminal

## Observabilidade

Toda a interação está no CloudWatch. Pra ver o tráfego MCP em tempo real:

```bash
# Em outro terminal CloudShell ou no console
aws logs tail /aws/lambda/field-notes-mcp-dev --follow
```

Vai mostrar cada `tools/call` chegando, com o `order_id` solicitado.

## Customizando

- **Outra pergunta**: altere a string em `question = ...` no `main()`
- **Outro modelo**: troque `claude-haiku-4-5-20251001-v1:0` por `claude-sonnet-4-5-20250929-v1:0` (melhor qualidade, ~10x mais caro)
- **Multi-turno**: substitua a chamada única `agent(question)` por um `while` lendo `input()`

## Troubleshooting

| Erro | Causa provável | Solução |
|---|---|---|
| `MCP_SERVER_URL não definida` | export não foi feito | rode o `aws cloudformation describe-stacks` acima |
| `AccessDeniedException InvokeModel` | Bedrock model access não habilitado | console AWS → Bedrock → Model access → habilitar Haiku 4.5 em us-east-1 |
| `503 Service Unavailable` | Lambda cold start expirou | rode de novo, segunda chamada pega container quente |
| `ModuleNotFoundError: strands` | venv não ativado | `source .venv/bin/activate` |
| `ConnectionError: streamable-http` | MCP_SERVER_URL apontando pra URL inválida | confirme o `echo $MCP_SERVER_URL` |
