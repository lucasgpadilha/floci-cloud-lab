locals {
  app_permissions_policy             = jsondecode(file("${path.module}/policy-documents/app-permissions.json"))
  educational_explicit_denies_policy = jsondecode(file("${path.module}/policy-documents/educational-explicit-denies.json"))
}
