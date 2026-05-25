# Terraform Local Validation

## Principle

Terraform targets Floci by default, not real AWS.

The local environment lives in:

```text
infra/envs/local
```

It uses modules from:

```text
infra/modules
```

## Current local resources

Phase 2 models these local emulated resources:

- S3 bucket for object storage.
- DynamoDB table for metadata using `pk` and `sk` keys.
- CloudWatch Logs log group for application logs.

## Provider safety

The local AWS provider uses fake credentials and explicit endpoint overrides pointing at:

```text
http://localhost:4566
```

The local endpoint variable validates that only `localhost` or `127.0.0.1` can be used.

## Safe commands

```bash
make terraform-fmt
make terraform-init-local
make terraform-validate
make terraform-plan-local
```

Equivalent raw commands:

```bash
terraform -chdir=infra/envs/local fmt -recursive ../..
terraform -chdir=infra/envs/local init -backend=false
terraform -chdir=infra/envs/local validate
terraform -chdir=infra/envs/local plan
```

## Local apply policy

`terraform apply` is acceptable only when all of these are true:

1. The working directory is `infra/envs/local`.
2. Provider endpoints are explicitly local Floci endpoints.
3. Credentials are fake local values.
4. Floci is running locally.
5. The operator states that this is an emulator-only apply.

Any apply against real AWS is prohibited without explicit human approval.
