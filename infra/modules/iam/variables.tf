variable "policy_owner" {
  description = "Human-readable owner of the educational IAM policy documents."
  type        = string
  default     = "Floci Cloud Lab"
}

variable "runtime_boundary" {
  description = "Runtime boundary these policy documents are designed to explain."
  type        = string
  default     = "local Floci emulator only"
}
