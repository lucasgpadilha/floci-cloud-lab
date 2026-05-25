variable "project" {
  description = "Project name used for resource names and tags."
  type        = string
  default     = "floci-cloud-lab"
}

variable "environment" {
  description = "Environment name. The default local environment targets Floci, not real AWS."
  type        = string
  default     = "local"

  validation {
    condition     = contains(["local", "dev-template", "prod-template"], var.environment)
    error_message = "Environment must be local, dev-template, or prod-template."
  }
}

variable "aws_region" {
  description = "AWS region value used by SDKs and the AWS provider. Floci accepts any region."
  type        = string
  default     = "us-east-1"
}

variable "aws_endpoint_url" {
  description = "Local Floci endpoint. This must remain localhost for the local environment."
  type        = string
  default     = "http://localhost:4566"

  validation {
    condition     = can(regex("^http://(localhost|127[.]0[.]0[.]1)(:[0-9]+)?/?$", var.aws_endpoint_url))
    error_message = "The local environment endpoint must target localhost or 127.0.0.1."
  }
}

variable "name_prefix" {
  description = "Prefix for local emulated resources."
  type        = string
  default     = "floci-cloud-lab"
}

variable "log_retention_days" {
  description = "CloudWatch log retention used in local emulation and documented for real AWS."
  type        = number
  default     = 7
}

variable "tags" {
  description = "Additional tags for resources that support tagging in the emulator."
  type        = map(string)
  default     = {}
}
