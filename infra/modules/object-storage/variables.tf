variable "bucket_name" {
  description = "S3 bucket name."
  type        = string
}

variable "tags" {
  description = "Tags for supported resources."
  type        = map(string)
  default     = {}
}
