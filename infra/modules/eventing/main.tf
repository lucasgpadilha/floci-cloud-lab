# Phase 6 event-driven architecture notes.
#
# The current local implementation uses a DynamoDB-compatible outbox/event-log item
# in the existing metadata table to avoid unapproved local Terraform mutations.
# Future approved local migrations can add SQS/SNS/EventBridge-style resources here.

locals {
  modeled_event_flow = [
    "POST /objects",
    "ObjectCreated outbox event",
    "GET /events pending backlog",
    "POST /events/process local worker",
  ]
}

output "modeled_event_flow" {
  description = "Documentation-only local event flow for the Phase 6 portfolio milestone."
  value       = local.modeled_event_flow
}
