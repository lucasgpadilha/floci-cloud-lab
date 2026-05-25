output "floci_endpoint" {
  description = "Local Floci endpoint used by this Terraform environment."
  value       = var.aws_endpoint_url
}

output "object_bucket_name" {
  description = "Name of the local emulated S3 bucket for objects."
  value       = module.object_storage.bucket_name
}

output "metadata_table_name" {
  description = "Name of the local emulated DynamoDB metadata table."
  value       = module.database.table_name
}

output "app_log_group_name" {
  description = "Name of the local emulated CloudWatch Logs log group."
  value       = module.observability.log_group_name
}
