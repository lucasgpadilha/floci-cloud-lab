# App Demo Evidence

Timestamp: 2026-05-25T00:49:19Z

Worktree:

`/home/lucas/agentic/runs/floci-cloud-lab-codex`

## Implemented app surface

Backend:

- `GET /health`
- `POST /objects`
- `GET /objects`
- `GET /objects/{id}`

Storage flow:

- Object content is written to the Floci S3-compatible bucket `floci-cloud-lab-local-objects`.
- Object metadata is written to the Floci DynamoDB-compatible table `floci-cloud-lab-local-metadata`.

Frontend:

- Static polished browser UI at `app/frontend/index.html`.
- Talks to the local HTTP API adapter at `http://127.0.0.1:8080`.

Local adapters:

- `make app-demo` invokes the Lambda-style handler directly.
- `make app-api-local` starts a small stdlib HTTP adapter for browser/curl testing.

## Validation

Commands run:

```bash
make check
make app-demo
make terraform-plan-local
make app-api-local
curl http://127.0.0.1:8080/health
curl -H 'content-type: application/json' -H 'x-floci-user: curl-demo' \
  -d '{"name":"curl-demo.txt","content":"hello via local http adapter","metadata":{"source":"curl"}}' \
  http://127.0.0.1:8080/objects
```

Results:

```text
9 passed
Terraform: No changes. Your infrastructure matches the configuration.
GET /health -> 200
POST /objects -> 201
```

Example created object:

```text
object_id = obj_0ec2f2a5f83d456798eed8fcb41d5de9
owner_id = curl-demo
s3_bucket = floci-cloud-lab-local-objects
s3_key = objects/curl-demo/obj_0ec2f2a5f83d456798eed8fcb41d5de9/curl-demo.txt
```

## Safety

- Local Floci endpoint only: `http://localhost:4566`.
- Local HTTP adapter only: `http://127.0.0.1:8080`.
- Fake AWS credentials only.
- No commit, push, merge, rebase, or real AWS mutation.
