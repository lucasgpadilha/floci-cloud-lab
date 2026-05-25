# API Gateway and Lambda Proficiency

This phase evolves the local HTTP adapter into a production-shaped serverless API design while keeping the default workflow local-only.

## Local implementation

The application keeps business logic in the Lambda-style handler:

```text
app/backend/functions/api.py
```

The local server remains a thin adapter:

```text
app/backend/local_server.py
```

The adapter converts local HTTP requests into API Gateway HTTP API v2-shaped events and forwards them to `lambda_handler`. It does not duplicate route logic.

## Contract

OpenAPI document:

```text
docs/openapi/floci-cloud-lab-http-api.yaml
```

Current routes:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service health and portfolio metadata. |
| GET | `/objects` | List object metadata for the local caller. |
| POST | `/objects` | Store content in S3-compatible storage and metadata in DynamoDB-compatible storage. |
| GET | `/objects/{object_id}` | Fetch object metadata and content. |
| OPTIONS | `/objects` | CORS preflight behavior. |
| POST | `/async/jobs` | Future async placeholder for event-driven phases. |

## Response envelope

Success responses include:

```json
{
  "data": {},
  "request_id": "..."
}
```

The health endpoint keeps its simple portfolio shape and also includes `request_id`:

```json
{
  "ok": true,
  "service": "floci-cloud-lab-api",
  "runtime": "local-floci",
  "version": "0.1.0",
  "request_id": "..."
}
```

Error responses use a consistent envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "name is required and must be a non-empty string"
  },
  "request_id": "..."
}
```

## Request validation

`POST /objects` validates:

- `content-type` must be `application/json`;
- body must be valid JSON object;
- `name` is required and non-empty;
- `content` is required and must be a string;
- `content` must be 256 KB or smaller;
- `content_type`, when provided, must look like a media type;
- `metadata`, when provided, must be a JSON object.

## CORS behavior

The Lambda-style handler returns API Gateway-compatible CORS headers:

```text
access-control-allow-origin: *
access-control-allow-methods: GET,POST,OPTIONS
access-control-allow-headers: content-type,x-floci-user,x-request-id
access-control-expose-headers: x-request-id
```

This matches the local browser demo and documents what a future API Gateway HTTP API CORS config should allow.

## REST API vs HTTP API

For a future real AWS version, HTTP API is the natural default for this project:

| Topic | REST API | HTTP API |
| --- | --- | --- |
| Cost/latency | Older, more features, generally higher cost | Lower cost/latency for common APIs |
| Payload shape | API Gateway REST event shape | HTTP API v2 event shape |
| Use case | Complex mapping templates, API keys, usage plans | Simple Lambda-backed JSON API |
| Fit for this lab | Useful to learn later | Best current fit |

## Stages

The local adapter behaves like a `$default` HTTP API stage. A real AWS version would likely use:

- `$default` for a simple portfolio demo;
- `dev` for a sandbox account;
- `prod` only after explicit real AWS approval.

## Authorizers

The current lab uses `x-floci-user` as a local caller identity header. This is not real authentication.

Real AWS options to evaluate later:

- JWT authorizer for Cognito or another OIDC provider;
- Lambda authorizer for custom auth logic;
- IAM auth for machine-to-machine calls.

## Throttling

Local tests do not enforce API Gateway throttling. A real deployment should document route-level throttles, account limits, and client retry behavior.

## Contract tests

Contract tests live in:

```text
tests/contract/test_api_contract.py
```

They invoke the handler with API Gateway HTTP API v2-shaped events and assert:

- response status codes;
- `isBase64Encoded` shape;
- CORS headers;
- `x-request-id` propagation;
- consistent error envelopes;
- owner identity from `x-floci-user`.

## Local validation

Use:

```bash
make check
make devops-audit
make app-demo
```

The default workflow remains local Floci only. No real API Gateway, Lambda, IAM, or AWS account resources are created by this phase.
