variable "table_name" {
  description = "DynamoDB table name."
  type        = string
}

variable "tags" {
  description = "Tags for supported resources."
  type        = map(string)
  default     = {}
}
