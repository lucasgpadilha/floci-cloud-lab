# Evidence: DynamoDB proficiency

Phase 4 adds DynamoDB-focused data modeling and API behavior while staying local-first.

## Scope

Implemented in this phase:

- Metadata records now include:
  - owner/object primary key shape
  - `category`
  - modeled GSI projection fields: `gsi1pk`, `gsi1sk`
  - `version` for optimistic-concurrency update paths
  - optional `expires_at` epoch timestamp for TTL modeling
  - `ttl_status`
- Object creation uses a DynamoDB conditional write:
  - `attribute_not_exists(pk) AND attribute_not_exists(sk)`
- `GET /objects` supports:
  - `limit`
  - `cursor`
  - `category`
- Local HTTP adapter now forwards query string parameters into the Lambda event shape.
- Docs explain access patterns, partition/sort keys, GSI trade-offs, TTL, conditional writes, hot partitions, and emulator support gaps.

## Commands run

```bash
.venv/bin/python -m pytest tests/unit/test_dynamodb_model.py -q
.venv/bin/python -m pytest tests/contract/test_api_pagination_contract.py tests/unit/test_api_handler.py tests/unit/test_dynamodb_model.py -q
.venv/bin/python -m pytest tests -q
```

Observed result during implementation:

```text
30 passed
```

Final validation run on 2026-05-25:

```bash
make check
make app-demo
make devops-audit
```

Observed result:

```text
make check: docs-check ok, Terraform validate ok, 30 passed
make app-demo: GET /health 200, POST /objects 201, GET /objects 200, GET /objects/{id} 200
make devops-audit: terraform plan has no drift, 30 passed, local-only DevOps audit passed
```

## Important local migration note

`infra/modules/database/main.tf` documents the Phase 4 GSI/TTL model, but the physical local table is not migrated in this change. Adding a real `gsi1` and TTL block would require a Terraform apply against local Floci. This repo requires explicit approval before any apply, even local-only applies.

The repository therefore attempts the modeled `gsi1` category query and falls back to the owner partition query plus category filtering when the local table does not have the optional index.

## Files

```text
app/backend/functions/repository.py
app/backend/functions/api.py
app/backend/local_server.py
app/frontend/index.html
docs/dynamodb-data-model.md
docs/openapi/floci-cloud-lab-http-api.yaml
tests/unit/test_dynamodb_model.py
tests/contract/test_api_pagination_contract.py
tests/integration/test_app_floci_integration.py
infra/modules/database/main.tf
```
