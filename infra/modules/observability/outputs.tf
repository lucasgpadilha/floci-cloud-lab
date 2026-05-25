output "log_group_name" {
  description = "CloudWatch Logs log group name."
  value       = aws_cloudwatch_log_group.app.name
}
