# ADR 0002: Local-First Terraform Validation

## Status

Accepted.

## Context

The lab needs IaC practice but must avoid real AWS cost.

## Decision

Use Terraform against Floci as the default environment. Real AWS dev/prod environments may exist as templates later, but they are not default execution targets.

## Consequences

Positive:

- Terraform skills are demonstrated safely.
- Plans and applies can be validated locally.
- Resource modules can be developed iteratively.

Trade-offs:

- Provider endpoint overrides require careful configuration.
- Not every AWS provider resource may be fully supported by Floci.
