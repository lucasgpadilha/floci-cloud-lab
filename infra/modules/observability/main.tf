resource "aws_cloudwatch_log_group" "app" {
  name              = var.log_group_name
  retention_in_days = var.log_retention_days
  tags              = var.tags
}


# Phase 7 observability modeling notes:
# - The app emits structured JSON logs and CloudWatch-style metric records locally.
# - Physical CloudWatch metric filters, alarms, and dashboards are intentionally not
#   added yet because that would require an approved local Terraform migration/apply.
# - Future approved resources can model high 5xx rate, high latency, event backlog,
#   and DLQ count alarms. See docs/observability-deep-dive.md.
