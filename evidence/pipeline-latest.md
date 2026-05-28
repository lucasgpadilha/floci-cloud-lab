# Local Pipeline Evidence

- Captured at: `2026-05-28T22:05:44Z`
- Worktree: `/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12`
- Endpoint policy: local Floci only (`http://localhost:4566`)
- Credential policy: fake local credentials only; secret-looking values are redacted.
- Exclusions: this script does not collect `.env`, `.terraform/`, `*.tfstate`, `.venv/`, cache directories, or full environment dumps.
- Terraform safety: validation and plan are allowed; `terraform apply` is not run by this capture.


## Git status before evidence capture

- Started: `2026-05-28T22:05:44Z`
- Command: `git status --short`

```text
 M Makefile
 M README.md
 M docs/project-status.md
 M scripts/devops-audit.sh
?? docs/agentic-delivery-workflow.md
?? docs/release-process.md
?? evidence/pipeline-latest.md
?? scripts/capture-evidence.sh
?? tests/integration/conftest.py
?? tests/unit/test_local_pipeline_evidence.py
```

- Finished: `2026-05-28T22:05:44Z`
- Exit code: `0`


## Canonical local CI pipeline

- Started: `2026-05-28T22:05:44Z`
- Command: `make pipeline`

```text
make[1]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[1/13]: make docs-check
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
docs-check: ok
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[2/13]: make no-forbidden-ci
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
no-forbidden-ci: ok
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[3/13]: make local-endpoint-check
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
local-endpoint-check: ok
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[4/13]: make shell-check
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
shell-check: ok
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[5/13]: make compose-validate
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
docker compose config --quiet
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[6/13]: make compose-container-validate
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
docker compose -f compose.container.yaml config --quiet
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[7/13]: make k8s-validate
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
./scripts/k8s-validate.sh
static-yaml-check: ok (10 files)
kubectl-kustomize: skipped (kubectl not installed)
k8s-validate: ok
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[8/13]: make terraform-fmt
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[9/13]: make terraform-validate
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
terraform -chdir=infra/envs/local init -backend=false
[0m[1mInitializing modules...[0m
[0m[1mInitializing provider plugins...[0m
- Reusing previous version of hashicorp/aws from the dependency lock file
- Using previously-installed hashicorp/aws v5.100.0

[0m[1m[32mTerraform has been successfully initialized![0m[32m[0m
[0m[32m
You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.[0m
terraform -chdir=infra/envs/local validate
[32m[1mSuccess![0m The configuration is valid.
[0m
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[10/13]: make python-test
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
......ssss.............................................................. [100%]
68 passed, 4 skipped in 0.35s
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[11/13]: make floci-health
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
./scripts/floci-health.sh
floci-health: ok (http://localhost:4566/_localstack/health)
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[12/13]: make floci-smoke
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
...                                                                      [100%]
3 passed in 0.27s
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline[13/13]: make terraform-plan-local
make[2]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
terraform -chdir=infra/envs/local plan

Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  [32m+[0m create[0m

Terraform will perform the following actions:

[1m  # module.database.aws_dynamodb_table.metadata[0m will be created
[0m  [32m+[0m[0m resource "aws_dynamodb_table" "metadata" {
      [32m+[0m[0m arn              = (known after apply)
      [32m+[0m[0m billing_mode     = "PAY_PER_REQUEST"
      [32m+[0m[0m hash_key         = "pk"
      [32m+[0m[0m id               = (known after apply)
      [32m+[0m[0m name             = "floci-cloud-lab-local-metadata"
      [32m+[0m[0m range_key        = "sk"
      [32m+[0m[0m read_capacity    = (known after apply)
      [32m+[0m[0m stream_arn       = (known after apply)
      [32m+[0m[0m stream_label     = (known after apply)
      [32m+[0m[0m stream_view_type = (known after apply)
      [32m+[0m[0m tags             = {
          [32m+[0m[0m "CostCenter"  = "PersonalCloudLab"
          [32m+[0m[0m "Environment" = "local"
          [32m+[0m[0m "ManagedBy"   = "Terraform"
          [32m+[0m[0m "Owner"       = "Lucas"
          [32m+[0m[0m "Project"     = "FlociCloudLab"
          [32m+[0m[0m "Runtime"     = "FlociLocal"
        }
      [32m+[0m[0m tags_all         = {
          [32m+[0m[0m "CostCenter"  = "PersonalCloudLab"
          [32m+[0m[0m "Environment" = "local"
          [32m+[0m[0m "ManagedBy"   = "Terraform"
          [32m+[0m[0m "Owner"       = "Lucas"
          [32m+[0m[0m "Project"     = "FlociCloudLab"
          [32m+[0m[0m "Runtime"     = "FlociLocal"
        }
      [32m+[0m[0m write_capacity   = (known after apply)

      [32m+[0m[0m attribute {
          [32m+[0m[0m name = "pk"
          [32m+[0m[0m type = "S"
        }
      [32m+[0m[0m attribute {
          [32m+[0m[0m name = "sk"
          [32m+[0m[0m type = "S"
        }

      [32m+[0m[0m point_in_time_recovery (known after apply)

      [32m+[0m[0m server_side_encryption (known after apply)

      [32m+[0m[0m ttl (known after apply)
    }

[1m  # module.object_storage.aws_s3_bucket.objects[0m will be created
[0m  [32m+[0m[0m resource "aws_s3_bucket" "objects" {
      [32m+[0m[0m acceleration_status         = (known after apply)
      [32m+[0m[0m acl                         = (known after apply)
      [32m+[0m[0m arn                         = (known after apply)
      [32m+[0m[0m bucket                      = "floci-cloud-lab-local-objects"
      [32m+[0m[0m bucket_domain_name          = (known after apply)
      [32m+[0m[0m bucket_prefix               = (known after apply)
      [32m+[0m[0m bucket_regional_domain_name = (known after apply)
      [32m+[0m[0m force_destroy               = false
      [32m+[0m[0m hosted_zone_id              = (known after apply)
      [32m+[0m[0m id                          = (known after apply)
      [32m+[0m[0m object_lock_enabled         = (known after apply)
      [32m+[0m[0m policy                      = (known after apply)
      [32m+[0m[0m region                      = (known after apply)
      [32m+[0m[0m request_payer               = (known after apply)
      [32m+[0m[0m tags                        = {
          [32m+[0m[0m "CostCenter"  = "PersonalCloudLab"
          [32m+[0m[0m "Environment" = "local"
          [32m+[0m[0m "ManagedBy"   = "Terraform"
          [32m+[0m[0m "Owner"       = "Lucas"
          [32m+[0m[0m "Project"     = "FlociCloudLab"
          [32m+[0m[0m "Runtime"     = "FlociLocal"
        }
      [32m+[0m[0m tags_all                    = {
          [32m+[0m[0m "CostCenter"  = "PersonalCloudLab"
          [32m+[0m[0m "Environment" = "local"
          [32m+[0m[0m "ManagedBy"   = "Terraform"
          [32m+[0m[0m "Owner"       = "Lucas"
          [32m+[0m[0m "Project"     = "FlociCloudLab"
          [32m+[0m[0m "Runtime"     = "FlociLocal"
        }
      [32m+[0m[0m website_domain              = (known after apply)
      [32m+[0m[0m website_endpoint            = (known after apply)

      [32m+[0m[0m cors_rule (known after apply)

      [32m+[0m[0m grant (known after apply)

      [32m+[0m[0m lifecycle_rule (known after apply)

      [32m+[0m[0m logging (known after apply)

      [32m+[0m[0m object_lock_configuration (known after apply)

      [32m+[0m[0m replication_configuration (known after apply)

      [32m+[0m[0m server_side_encryption_configuration (known after apply)

      [32m+[0m[0m versioning (known after apply)

      [32m+[0m[0m website (known after apply)
    }

[1m  # module.object_storage.aws_s3_bucket_versioning.objects[0m will be created
[0m  [32m+[0m[0m resource "aws_s3_bucket_versioning" "objects" {
      [32m+[0m[0m bucket = (known after apply)
      [32m+[0m[0m id     = (known after apply)

      [32m+[0m[0m versioning_configuration {
          [32m+[0m[0m mfa_delete = (known after apply)
          [32m+[0m[0m status     = "Enabled"
        }
    }

[1m  # module.observability.aws_cloudwatch_log_group.app[0m will be created
[0m  [32m+[0m[0m resource "aws_cloudwatch_log_group" "app" {
      [32m+[0m[0m arn               = (known after apply)
      [32m+[0m[0m id                = (known after apply)
      [32m+[0m[0m log_group_class   = (known after apply)
      [32m+[0m[0m name              = "/floci-cloud-lab/local/app"
      [32m+[0m[0m name_prefix       = (known after apply)
      [32m+[0m[0m retention_in_days = 7
      [32m+[0m[0m skip_destroy      = false
      [32m+[0m[0m tags              = {
          [32m+[0m[0m "CostCenter"  = "PersonalCloudLab"
          [32m+[0m[0m "Environment" = "local"
          [32m+[0m[0m "ManagedBy"   = "Terraform"
          [32m+[0m[0m "Owner"       = "Lucas"
          [32m+[0m[0m "Project"     = "FlociCloudLab"
          [32m+[0m[0m "Runtime"     = "FlociLocal"
        }
      [32m+[0m[0m tags_all          = {
          [32m+[0m[0m "CostCenter"  = "PersonalCloudLab"
          [32m+[0m[0m "Environment" = "local"
          [32m+[0m[0m "ManagedBy"   = "Terraform"
          [32m+[0m[0m "Owner"       = "Lucas"
          [32m+[0m[0m "Project"     = "FlociCloudLab"
          [32m+[0m[0m "Runtime"     = "FlociLocal"
        }
    }

[1mPlan:[0m 4 to add, 0 to change, 0 to destroy.
[0m
Changes to Outputs:
  [32m+[0m[0m app_log_group_name  = "/floci-cloud-lab/local/app"
  [32m+[0m[0m floci_endpoint      = "http://localhost:4566"
  [32m+[0m[0m metadata_table_name = "floci-cloud-lab-local-metadata"
  [32m+[0m[0m object_bucket_name  = "floci-cloud-lab-local-objects"
[90m
─────────────────────────────────────────────────────────────────────────────[0m

Note: You didn't use the -out option to save this plan, so Terraform can't
guarantee to take exactly these actions if you run "terraform apply" now.
make[2]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
pipeline: ok
make[1]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
```

- Finished: `2026-05-28T22:05:57Z`
- Exit code: `0`


## Compatibility check target

- Started: `2026-05-28T22:05:57Z`
- Command: `make check`

```text
make[1]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
docs-check: ok
no-forbidden-ci: ok
./scripts/k8s-validate.sh
static-yaml-check: ok (10 files)
kubectl-kustomize: skipped (kubectl not installed)
k8s-validate: ok
terraform -chdir=infra/envs/local init -backend=false
[0m[1mInitializing modules...[0m
[0m[1mInitializing provider plugins...[0m
- Reusing previous version of hashicorp/aws from the dependency lock file
- Using previously-installed hashicorp/aws v5.100.0

[0m[1m[32mTerraform has been successfully initialized![0m[32m[0m
[0m[32m
You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.[0m
terraform -chdir=infra/envs/local validate
[32m[1mSuccess![0m The configuration is valid.
[0m
......ssss.............................................................. [100%]
68 passed, 4 skipped in 0.35s
make[1]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
```

- Finished: `2026-05-28T22:06:03Z`
- Exit code: `0`


## Whitespace diff check

- Started: `2026-05-28T22:06:03Z`
- Command: `git diff --check`

```text
```

- Finished: `2026-05-28T22:06:03Z`
- Exit code: `0`


## Forbidden hosted CI guard

- Started: `2026-05-28T22:06:03Z`
- Command: `make no-forbidden-ci`

```text
make[1]: Entering directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
no-forbidden-ci: ok
make[1]: Leaving directory '/home/lucas/agentic/runs/floci-cloud-lab-codex-phase12'
```

- Finished: `2026-05-28T22:06:03Z`
- Exit code: `0`
