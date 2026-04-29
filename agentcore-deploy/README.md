# AgentCore deploy (reference Terraform)

Reference Terraform for the infrastructure that runs a Strands agent on AWS AgentCore.

## What it provisions

- CloudWatch Logs group with configurable retention
- IAM execution role with least-privilege access to specific Bedrock models
- Resource-level naming consistent with multi-environment deployments
- (Commented in `main.tf`) AgentCore agent runtime resource — uncomment to deploy

## Pré-requisitos

⚠️ **Atenção: dependendo do ambiente, você precisa instalar Terraform manualmente.**

### CloudShell (Amazon Linux 2023)

CloudShell **não traz Terraform pré-instalado**. Instale pelo repositório oficial da HashiCorp:

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo dnf install -y terraform
terraform --version
```

⚠️ **Pegadinha do CloudShell — espaço em disco:**

CloudShell tem apenas **1GB de armazenamento persistente em `/home`**. O provider AWS do Terraform sozinho ocupa ~600MB. Se você já criou venvs Python neste home (Strands, MCP, etc), o `terraform init` pode falhar com `no space left on device`.

Se acontecer, libere espaço antes de tentar de novo:

```bash
# Remove caches que não são mais necessários
rm -rf ~/.cache/pip
sudo dnf clean all

# Remove .aws-sam build cache se já fez deploy do mcp-lambda
rm -rf ~/aws-agentic-stack-starter/mcp-lambda/.aws-sam

# Confere espaço
df -h /home
```

Para esta demo, é mais prático **rodar `terraform plan` localmente** (na sua máquina, fora do CloudShell). Não há custo, não há lock de estado remoto, e você evita o problema de espaço.

### Local (Windows/macOS/Linux)

- [Terraform 1.7+](https://developer.hashicorp.com/terraform/install)
- AWS CLI v2 configurado com credenciais
- Bedrock model access garantido na região alvo

## Apply (referência — não execute durante a demo)

⚠️ **Importante:** o bloco `aws_bedrockagentcore_agent_runtime` em `main.tf` está **comentado de propósito**. Para a demo, rode apenas `terraform plan`. AgentCore Runtime cobra por sessão e CPU — `terraform apply` sem destroy depois acumula custo.

```bash
cd agentcore-deploy
terraform init
terraform plan -var="environment=dev"

# Esperado: Plan: 3 to add, 0 to change, 0 to destroy.
#   - aws_cloudwatch_log_group.agent_runtime
#   - aws_iam_role.agent_runtime
#   - aws_iam_role_policy.agent_runtime
```

Para deployar em produção (fora do escopo da demo):

1. Descomente o bloco `aws_bedrockagentcore_agent_runtime` em `main.tf`
2. Build do container ARM64 (Graviton) com seu código de agente
3. Push para ECR
4. Atualize `var.container_image_uri` para apontar para o ECR
5. `terraform apply -var="environment=dev"`
6. **Não esqueça do `terraform destroy` quando terminar testes** — Runtime cobra por uso

## Variáveis principais

| Variable | Default | Comentário |
|----------|---------|------------|
| `aws_region` | `us-east-1` | Mude para a região onde Bedrock está habilitado |
| `allowed_bedrock_models` | Haiku 4.5 + Sonnet 4.5 | Whitelist explícita — princípio de menor privilégio |
| `log_retention_days` | 30 | Compliance pode exigir 365+ |
| `environment` | `dev` | Sempre passe explicitamente em CI |

## Boas práticas que valem destacar

O `main.tf` aplica três padrões importantes que muito Terraform por aí esquece:

1. **`aws:SourceAccount` condition** no trust policy — proteção contra confused deputy attack
2. **Recursos Bedrock por ARN específico**, não wildcard — só os modelos da whitelist são invocáveis
3. **Log group dedicado** — observabilidade não mistura com outros workloads

## Notas sobre AgentCore Runtime (estado em Abril/2026)

- GA do Runtime: outubro/2025
- GA de Policy e Evaluations: março/2026
- Suporta MCP server stateless desde dezembro/2025; stateful (microVM dedicada) desde março/2026
- Container precisa ser **ARM64 (Graviton)** — exigência do runtime. Build com `--platform linux/arm64` se estiver em x86.
- Disponível em: us-east-1, us-east-2, us-west-2, ap-south-1, ap-southeast-1, ap-southeast-2, ap-northeast-1, eu-central-1, eu-west-1
- **Não disponível em sa-east-1** ainda

## References

- [Amazon Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [Terraform AWS provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
