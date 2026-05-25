# Evidence: S3 object storage

Phase 5 adds S3-focused object storage patterns beyond basic put/get while staying local-first.

## Scope

Implemented in this phase:

- Safe object key convention:
  - `objects/<safe-owner-id>/<object-id>/<safe-filename>`
- Content type preservation on upload and retrieval.
- S3 metadata persistence:
  - `owner-id`
  - `object-id`
  - `sha256`
  - `user-*` request metadata values
- SHA-256 object integrity metadata written to both S3 and DynamoDB metadata.
- Retrieval integrity verification via recomputed SHA-256.
- Local presigned GET URL generation via boto3.
- Documentation for versioning, lifecycle, multipart upload, bucket policies, encryption, public access block, events, replication, and cost drivers.

## Commands run during implementation

```bash
.venv/bin/python -m pytest tests/unit/test_s3_storage_model.py -q
.venv/bin/python -m pytest tests/integration/test_s3_patterns.py -q
.venv/bin/python -m pytest tests -q
```

Observed result:

```text
34 passed
```

Final validation run on 2026-05-25:

```bash
make check
make app-demo
make devops-audit
```

Observed result:

```text
make check: docs-check ok, Terraform validate ok, 34 passed
make app-demo: GET /health 200, POST /objects 201 with sha256 and s3_version_id, GET /objects 200, GET /objects/{id} 200 with integrity_verified=true
make devops-audit: terraform plan has no drift, 34 passed, local-only DevOps audit passed
```

## Important local migration note

`infra/modules/object-storage/main.tf` documents production S3 hardening options, but this change does not add new physical Terraform resources such as lifecycle configuration, public access block, default encryption, or bucket policy. Adding those would require a local Terraform apply/migration, and this repo requires explicit approval before any apply, even local-only applies.

The current local bucket already has versioning enabled from the baseline Terraform apply. The app records returned S3 version IDs when Floci returns them.

## Files

```text
app/backend/functions/storage.py
app/backend/functions/repository.py
docs/s3-object-storage.md
docs/openapi/floci-cloud-lab-http-api.yaml
evidence/s3-object-storage.md
infra/modules/object-storage/main.tf
tests/unit/test_s3_storage_model.py
tests/integration/test_s3_patterns.py
```
