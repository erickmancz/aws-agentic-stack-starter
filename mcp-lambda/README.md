# MCP Server em AWS Lambda

Implementação enxuta de um MCP server hospedado em AWS Lambda, exposto via Function URL com transporte streamable HTTP.

## O que este módulo demonstra

- Como o protocolo MCP funciona "por baixo" — JSON-RPC 2.0 manual, sem biblioteca pré-pronta
- Como hospedar um MCP server stateless em Lambda usando Function URL (sem precisar de API Gateway)
- Como conectar um cliente MCP (Strands) a um servidor remoto via streamable HTTP

## Por que Lambda Function URL e não API Gateway?

| Necessidade | API Gateway | Function URL |
|---|---|---|
| Endpoint HTTPS para o Lambda | ✓ | ✓ |
| Custom domain | ✓ | ⚠️ via CloudFront |
| Multi-tenant, rate limit por consumidor, WAF | ✓ | ✗ |
| Auth IAM (SigV4) | ✓ | ✓ |
| Auth Cognito | ✓ via Authorizer | ✗ |
| Custo extra além do Lambda | $1.00 / 1M req | $0 |

Para um MCP server consumido pelo seu próprio agente, na sua conta, sem necessidade de governar o tráfego, **Function URL é mais simples e barato**. Se virar API pública pra terceiros, migra pra API Gateway depois.

## Pré-requisitos

Esses pré-requisitos já estão satisfeitos no AWS CloudShell:

- AWS CLI v2 (CloudShell tem instalado)
- SAM CLI (CloudShell tem instalado)
- Python 3.11+ (CloudShell tem)
- Permissão para criar Lambda, IAM Role, CloudWatch Logs e Function URL na sua conta

## Deploy via CloudShell

```bash
# Clona o repo (no CloudShell)
git clone https://github.com/erickmancz/aws-agentic-stack-starter.git
cd aws-agentic-stack-starter/mcp-lambda

# Build e deploy interativo
sam build
sam deploy --guided
```

No `--guided`, responda:

| Pergunta | Resposta |
|---|---|
| Stack Name | `field-notes-mcp-demo` |
| AWS Region | `us-east-1` |
| Parameter EnvironmentName | `dev` |
| Parameter AuthType | `NONE` (demo) ou `AWS_IAM` (prod) |
| Confirm changes before deploy | `n` |
| Allow SAM CLI IAM role creation | `Y` |
| Disable rollback | `n` |
| Save arguments to configuration file | `Y` |

Após o deploy, copie o output `McpServerUrl` — é a URL que o agente Strands vai consumir.

```bash
# Pegando a URL via CLI:
aws cloudformation describe-stacks \
  --stack-name field-notes-mcp-demo \
  --query "Stacks[0].Outputs[?OutputKey=='McpServerUrl'].OutputValue" \
  --output text
```

Saída esperada:
```
https://abc123xyz.lambda-url.us-east-1.on.aws/
```

## Testando o MCP server diretamente

Antes de plugar o Strands, dá pra confirmar que o MCP server responde via `curl`:

```bash
MCP_URL=$(aws cloudformation describe-stacks \
  --stack-name field-notes-mcp-demo \
  --query "Stacks[0].Outputs[?OutputKey=='McpServerUrl'].OutputValue" \
  --output text)

# Health check (GET)
curl "$MCP_URL"

# tools/list (POST com JSON-RPC)
curl -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# tools/call
curl -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":2,
    "method":"tools/call",
    "params":{
      "name":"lookup_order_status",
      "arguments":{"order_id":"ORD-1002"}
    }
  }'
```

## Sobre o trade-off de auth

A demo usa `AuthType=NONE` para simplicidade. **Em produção real**, escolha entre:

- **`AWS_IAM`** — caller assina cada request com SigV4. Bom para clientes dentro da sua conta AWS (ex: outro Lambda, ECS, EC2). Sem dependência externa.
- **API Gateway na frente com Cognito Authorizer** — bom para clientes externos com OAuth.
- **AgentCore Gateway** — quando você quer gerenciamento total de auth + rate limit + transformação MCP.

A própria Anthropic recomenda OAuth 2.1 para MCP servers expostos publicamente — não use `NONE` em produção.

## Custo estimado

- **Lambda**: 1M invocações/mês grátis no free tier; demo usa ~30. Custo: $0.
- **CloudWatch Logs**: 5GB/mês grátis. Demo gera ~10MB. Custo: $0.
- **Function URL**: sem cobrança adicional além do Lambda.

Total da demo: **$0**.

## Cleanup

```bash
sam delete --stack-name field-notes-mcp-demo
```

Confirma com `Y`. Em ~30s todo o stack é removido.

## Estrutura

```
mcp-lambda/
├── handler.py        # Handler MCP — JSON-RPC 2.0 manual
├── template.yaml     # SAM template — Lambda + Function URL
├── requirements.txt  # Vazio (só stdlib)
└── README.md         # Este arquivo
```

## Próximos passos (caminho de produção)

1. **Persistência**: substituir `FAKE_ORDERS` por uma chamada DynamoDB via `boto3`.
2. **Auth**: trocar `AuthType=NONE` por `AWS_IAM` e fazer o cliente assinar com SigV4.
3. **Observabilidade**: adicionar OTEL exporter — vai pro CloudWatch via OpenTelemetry.
4. **Migração para AgentCore Runtime**: o mesmo container/handler pode ser empacotado e deployado em `aws_bedrockagentcore_agent_runtime` se você quiser stateful sessions.
