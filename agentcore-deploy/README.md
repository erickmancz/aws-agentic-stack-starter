# AgentCore deploy (reference Terraform)

Reference Terraform for the infrastructure that runs a Strands agent on AWS AgentCore.

## What it provisions

- CloudWatch Logs group with configurable retention
- IAM execution role with least-privilege access to specific Bedrock models
- Resource-level naming consistent with multi-environment deployments

## What it does NOT provision yet

- **The AgentCore runtime resource itself.** See the note in `main.tf` — the Terraform AWS provider's support for AgentCore is evolving. Deploy the runtime via AWS CLI or CloudFormation using the pattern in [agentcore-deploy.md](./agentcore-deploy.md) until the provider stabilizes.
- VPC endpoints for private Bedrock access (add when moving to production)
- Autoscaling, alarms, dashboards (production concerns)
- WAF in front of the agent endpoint (only needed if you expose it publicly)

> **Transparency:** AgentCore is new. Both the resource shape and the Terraform support will shift over the next few quarters. This module is scaffolding, not a turn-key production deployment. If something breaks when you apply it, open an issue.

## Prerequisites

- Terraform 1.7+
- AWS credentials with IAM, Logs, and Bedrock administrative permissions
- Bedrock model access granted in the target region

## Apply

```bash
cd agentcore-deploy
terraform init
terraform plan -var="environment=dev"
terraform apply -var="environment=dev"
```

## Variables you probably want to override

| Variable | Default | Why override |
|----------|---------|--------------|
| `aws_region` | `us-east-1` | Change to your preferred Bedrock-enabled region |
| `allowed_bedrock_models` | Claude 3.5 Sonnet + Haiku | Change to the specific models your agent uses — keep this list minimal |
| `log_retention_days` | 30 | Compliance may require longer (check your org's log retention policy) |
| `environment` | `dev` | Always set explicitly in CI |

## Teardown

```bash
terraform destroy -var="environment=dev"
```

## References

- [Amazon Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [Terraform AWS provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
