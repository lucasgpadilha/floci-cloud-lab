# IAM and Security Evidence

Captured: 2026-05-25T10:20:00-03:00
Worktree: `/home/lucas/agentic/runs/floci-cloud-lab-codex`
Scope: local policy-document validation only; no real AWS IAM mutation.

## Commands run

```bash
terraform -chdir=infra/envs/local fmt -recursive ../..
make check
make devops-audit
```

## Result summary

- Terraform formatting completed for the IAM module files.
- `make check` passed with `16 passed`.
- `make devops-audit` passed.
- IAM wildcard guard passed: exact `Action: "*"` and `Resource: "*"` patterns are not present in the IAM module policy documents.

## Policy documents validated

- `infra/modules/iam/policy-documents/app-permissions.json`
- `infra/modules/iam/policy-documents/educational-explicit-denies.json`

## Sanitized check excerpt

```text
docs-check: ok
no-forbidden-ci: ok
Success! The configuration is valid.
16 passed
```

## Sanitized DevOps audit excerpt

```text
== IAM wildcard policy guard ==
ok: IAM policy documents avoid exact wildcard Action/Resource
== terraform fmt/validate/drift ==
Success! The configuration is valid.
ok: terraform plan has no drift
== python tests ==
16 passed
== devops audit complete ==
ok: local-only DevOps audit passed
```

## Interpretation

Phase 2 adds IAM/security design artifacts without changing real AWS. The policy JSON is intentionally scoped to the local lab resources and the tests enforce no exact wildcard action/resource policies. The docs explain how the local design would translate to real AWS roles, trust policies, permission policies, explicit deny guardrails, and threat modeling.
