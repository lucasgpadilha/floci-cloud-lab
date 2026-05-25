output "app_permissions_policy_json" {
  description = "Least-privilege application permission policy as JSON."
  value       = jsonencode(local.app_permissions_policy)
}

output "educational_explicit_denies_policy_json" {
  description = "Educational explicit-deny guardrail policy as JSON."
  value       = jsonencode(local.educational_explicit_denies_policy)
}

output "policy_document_paths" {
  description = "Policy JSON documents shipped with this IAM module."
  value = {
    app_permissions             = "${path.module}/policy-documents/app-permissions.json"
    educational_explicit_denies = "${path.module}/policy-documents/educational-explicit-denies.json"
    policy_owner                = var.policy_owner
    runtime_boundary            = var.runtime_boundary
  }
}
