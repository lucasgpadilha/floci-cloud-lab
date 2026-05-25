# Local Apply Evidence

Timestamp: 2026-05-24T21:40:10-03:00

Worktree:

`/home/lucas/agentic/runs/floci-cloud-lab-codex`

## Scope

Terraform was applied only against the local Floci AWS-compatible emulator endpoint:

`http://localhost:4566`

No real AWS endpoint was used.

## Commands

```bash
make floci-up
make floci-health
make floci-smoke
terraform -chdir=infra/envs/local apply -auto-approve
make check
make terraform-plan-local
```

## Apply result

```text
Apply complete! Resources: 4 added, 0 changed, 0 destroyed.
```

Outputs:

```text
app_log_group_name = "/floci-cloud-lab/local/app"
floci_endpoint = "http://localhost:4566"
metadata_table_name = "floci-cloud-lab-local-metadata"
object_bucket_name = "floci-cloud-lab-local-objects"
```

## Post-apply validation

```text
floci-health: ok (http://localhost:4566/_localstack/health)
3 passed
Terraform configuration is valid.
No changes. Your infrastructure matches the configuration.
```

## Created local/emulated resources

- DynamoDB table: `floci-cloud-lab-local-metadata`
- S3 bucket: `floci-cloud-lab-local-objects`
- S3 bucket versioning: enabled
- CloudWatch log group: `/floci-cloud-lab/local/app`

## Safety guardrail added

The Makefile now includes `terraform-apply-local`, guarded so it only accepts:

- `http://localhost:4566`
- `http://127.0.0.1:4566`

This keeps the local apply workflow aligned with the project goal: portfolio AWS learning against Floci, not real AWS provisioning.
