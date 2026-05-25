variable "log_group_name" {
  description = "CloudWatch Logs log group name."
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention in days."
  type        = number
  default     = 7
}

variable "tags" {
  description = "Tags for supported resources."
  type        = map(string)
  default     = {}
}
