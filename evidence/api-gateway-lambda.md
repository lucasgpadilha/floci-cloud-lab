# API Gateway and Lambda Evidence

Captured: 2026-05-25T10:55:00-03:00
Worktree: `/home/lucas/agentic/runs/floci-cloud-lab-codex`
Scope: local Lambda-style handler and local HTTP adapter only; no real API Gateway or Lambda resources were created.

## Commands run

```bash
make check
make devops-audit
make app-demo
```

## Result summary

- `make check`: passed with `23 passed`.
- `make devops-audit`: passed with no Terraform drift.
- `make app-demo`: passed and returned request IDs in response bodies.
- Contract tests validated API Gateway HTTP API v2-shaped events.

## Artifacts validated

- `app/backend/functions/api.py`
- `app/backend/functions/auth.py`
- `app/backend/functions/errors.py`
- `app/backend/local_server.py`
- `docs/api-gateway-lambda.md`
- `docs/openapi/floci-cloud-lab-http-api.yaml`
- `tests/contract/test_api_contract.py`

## Sanitized check excerpt

```text
docs-check: ok
no-forbidden-ci: ok
Success! The configuration is valid.
23 passed
```

## Sanitized DevOps audit excerpt

```text
== IAM wildcard policy guard ==
ok: IAM policy documents avoid exact wildcard Action/Resource
== terraform fmt/validate/drift ==
Success! The configuration is valid.
ok: terraform plan has no drift
== python tests ==
23 passed
== devops audit complete ==
ok: local-only DevOps audit passed
```

## Sanitized app demo excerpt

```text
GET /health -> 200
request_id: local-request
POST /objects -> 201
request_id: local-request
GET /objects -> 200
GET /objects/{object_id} -> 200
```

## Interpretation

Phase 3 keeps the local server as a thin adapter and moves production-shaped behavior into the Lambda-style handler. The handler now supports API Gateway HTTP API v2 event shape, consistent request IDs, CORS responses, request validation, mapped error envelopes, OpenAPI documentation, and contract tests.
