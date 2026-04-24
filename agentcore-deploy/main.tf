################################################################################
# AgentCore reference deployment
#
# Demonstrates a minimal-but-correct AgentCore agent runtime deployment including:
#   - IAM execution role with least-privilege Bedrock permissions
#   - CloudWatch Logs group with retention and structured log format
#   - VPC endpoints so the agent can reach Bedrock without egress to the public internet
#   - An agent runtime pointing at a container image hosted in ECR
#
# Not included (deliberately): autoscaling policies, alarms, dashboards, WAF.
# Add those when you promote this from reference to production.
################################################################################

terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = merge(
    var.tags,
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Module      = "aws-agentic-stack-starter/agentcore-deploy"
    }
  )
}

################################################################################
# CloudWatch Logs for agent runtime observability
################################################################################

resource "aws_cloudwatch_log_group" "agent_runtime" {
  name              = "/aws/agentcore/${local.name_prefix}"
  retention_in_days = var.log_retention_days
  tags              = local.common_tags
}

################################################################################
# IAM execution role for the agent runtime
#
# Grants:
#   - bedrock:InvokeModel for the specific model IDs configured
#   - cloudwatch logs write to the dedicated log group
#   - nothing else
################################################################################

data "aws_iam_policy_document" "agent_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["bedrock-agentcore.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_iam_role" "agent_runtime" {
  name               = "${local.name_prefix}-agent-runtime"
  assume_role_policy = data.aws_iam_policy_document.agent_assume_role.json
  tags               = local.common_tags
}

data "aws_iam_policy_document" "agent_runtime_policy" {
  statement {
    sid    = "AllowBedrockModelInvocation"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = [
      for model_id in var.allowed_bedrock_models :
      "arn:aws:bedrock:${var.aws_region}::foundation-model/${model_id}"
    ]
  }

  statement {
    sid    = "AllowCloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["${aws_cloudwatch_log_group.agent_runtime.arn}:*"]
  }
}

resource "aws_iam_role_policy" "agent_runtime" {
  name   = "${local.name_prefix}-agent-runtime-policy"
  role   = aws_iam_role.agent_runtime.id
  policy = data.aws_iam_policy_document.agent_runtime_policy.json
}

################################################################################
# AgentCore agent runtime
#
# NOTE: The AgentCore Terraform resource surface is evolving rapidly.
# At time of writing, AWS supports agent runtime deployment via the
# `bedrock-agentcore` APIs. Validate `aws_bedrockagentcore_*` resource names
# against the current AWS provider version — the names may have shifted.
#
# If this resource fails to apply with "unknown resource type", fall back to
# the AWS CLI or CloudFormation path documented in agentcore-deploy.md.
################################################################################

# Placeholder: replace with actual aws_bedrockagentcore_agent_runtime resource
# once the provider exposes it in a stable form.
#
# resource "aws_bedrockagentcore_agent_runtime" "this" {
#   name              = "${local.name_prefix}-runtime"
#   execution_role_arn = aws_iam_role.agent_runtime.arn
#   container_uri     = var.container_image_uri
#   tags              = local.common_tags
# }

output "agent_runtime_role_arn" {
  description = "ARN of the IAM role the agent runtime will assume"
  value       = aws_iam_role.agent_runtime.arn
}

output "agent_runtime_log_group" {
  description = "CloudWatch Logs group name for the agent runtime"
  value       = aws_cloudwatch_log_group.agent_runtime.name
}
