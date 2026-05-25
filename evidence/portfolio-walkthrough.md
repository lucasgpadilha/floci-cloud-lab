# Portfolio Walkthrough Evidence

Captured: 2026-05-25T10:08:00-03:00
Worktree: `/home/lucas/agentic/runs/floci-cloud-lab-codex`
Endpoint boundary: local Floci only, `http://localhost:4566`
Credentials boundary: fake local credentials only (`test`/`test`).

## Commands run

```bash
make floci-up
make floci-health
make terraform-apply-local
make floci-smoke
make terraform-plan-local
make devops-audit
make app-demo
make check
```

## Result summary

- `make terraform-apply-local`: passed after explicit user approval; recreated 4 emulator-local resources.
- `make floci-health`: passed.
- `make floci-smoke`: passed.
- `make terraform-plan-local`: passed with no changes after apply.
- `make devops-audit`: passed.
- `make app-demo`: passed.
- `make check`: passed.

No real AWS credentials, real AWS endpoints, commit, push, merge, or rebase were used.

## Local resources recreated

- DynamoDB table: `floci-cloud-lab-local-metadata`
- S3 bucket: `floci-cloud-lab-local-objects`
- S3 bucket versioning: `floci-cloud-lab-local-objects`
- CloudWatch log group: `/floci-cloud-lab/local/app`

## Sanitized Terraform apply excerpt

```text
Apply complete! Resources: 4 added, 0 changed, 0 destroyed.
[0mapp_log_group_name = "/floci-cloud-lab/local/app"
floci_endpoint = "http://localhost:4566"
metadata_table_name = "floci-cloud-lab-local-metadata"
object_bucket_name = "floci-cloud-lab-local-objects"
```

## Sanitized smoke test excerpt

```text
3 passed in 0.31s
```

## Sanitized post-apply plan excerpt

```text
[0m[1m[32mNo changes.[0m[1m Your infrastructure matches the configuration.[0m
and found no differences, so no changes are needed.
```

## Sanitized DevOps audit excerpt

```text
== forbidden CI guard ==
ok: no forbidden CI files
== real AWS endpoint guard ==
ok: local Floci endpoint is explicit in operational files
ok: no real AWS endpoint patterns found
== shell syntax ==
ok: bash -n scripts/app-demo.sh
ok: bash -n scripts/devops-audit.sh
ok: bash -n scripts/floci-down.sh
ok: bash -n scripts/floci-env.sh
ok: bash -n scripts/floci-health.sh
ok: bash -n scripts/floci-up.sh
ok: bash -n scripts/smoke-test.sh
== docker compose validation ==
ok: docker compose config
== terraform fmt/validate/drift ==
ok: terraform plan has no drift
== python tests ==
12 passed in 0.33s
== devops audit complete ==
ok: local-only DevOps audit passed
```

## Sanitized app demo excerpt

```text
GET /health -> 200
  "runtime": "local-floci",
POST /objects -> 201
    "object_id": "obj_810f846f7d2444c5a9d659f5968a16b7",
GET /objects -> 200
        "object_id": "obj_810f846f7d2444c5a9d659f5968a16b7",
GET /objects/obj_810f846f7d2444c5a9d659f5968a16b7 -> 200
    "object_id": "obj_810f846f7d2444c5a9d659f5968a16b7",
```

## Sanitized `make check` excerpt

```text
docs-check: ok
no-forbidden-ci: ok
12 passed in 0.36s
```

## Interpretation

The local Floci environment is healthy, Terraform has recreated the expected emulator-local resources, the post-apply plan is idempotent, the local-only DevOps audit passes, and the application demo successfully exercises the Lambda-style handler, S3-compatible object storage, and DynamoDB-compatible metadata path.
