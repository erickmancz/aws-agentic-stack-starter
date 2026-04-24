variable "aws_region" {
  description = "AWS region where the agent runtime will be deployed."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short project identifier used as prefix for resource names."
  type        = string
  default     = "field-notes-week2"
}

variable "environment" {
  description = "Environment name: dev, stg, or prd."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "stg", "prd"], var.environment)
    error_message = "environment must be one of: dev, stg, prd."
  }
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention in days for the agent runtime log group."
  type        = number
  default     = 30
}

variable "allowed_bedrock_models" {
  description = "List of Bedrock foundation model IDs the agent is permitted to invoke."
  type        = list(string)
  default = [
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
  ]
}

variable "container_image_uri" {
  description = "ECR URI of the container image containing the Strands agent code."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags to apply to all resources."
  type        = map(string)
  default     = {}
}
