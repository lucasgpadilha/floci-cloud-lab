# Floci Studio Trace Debugger Evidence

- Captured at: `2026-06-01T01:39:16Z`
- Worktree: `/home/lucas/agentic/runs/floci-cloud-lab-gemini`
- API URL: `http://127.0.0.1:8080`
- Floci endpoint policy: local-only (`http://localhost:4566`)
- AWS SDK endpoint policy: local-only (`http://localhost:4566`)
- Owner namespace: `portfolio-evidence`
- Terraform safety: this capture never runs `terraform apply` or provisions resources automatically.
- Secret safety: output is sanitized before being written.

## What this proves

This evidence captures the Floci Studio differentiator: a local workflow debugger for AWS-shaped flows. The goal is not to show a generic resource dashboard; it is to show request → object storage → metadata → outbox event → processor result, including a deterministic broken flow and sanitized report export.

## Health check

- Started: `2026-06-01T01:39:16Z`
- Request: `GET http://127.0.0.1:8080/health`

```json
{
    "ok": true,
    "request_id": "local-e4de5e4012cf43d3bc1ed9036ce9afa2",
    "runtime": "local-floci",
    "service": "floci-cloud-lab-api",
    "version": "0.1.0"
}

```

- HTTP status: `200`
- Finished: `2026-06-01T01:39:16Z`


## Local session / capability discovery

- Started: `2026-06-01T01:39:16Z`
- Request: `GET http://127.0.0.1:8080/ops/session`

```json
{
    "adapter": {
        "account_id": "000000000000",
        "endpoint": "http://localhost:4566",
        "name": "floci",
        "region": "us-east-1",
        "runtime": "aws-compatible-local-emulator"
    },
    "capabilities": [
        {
            "description": "Correlate request, object, metadata, outbox, and processor state",
            "id": "flow-traces",
            "label": "Flow traces"
        },
        {
            "description": "Inspect local payloads and metadata without cloud credentials",
            "id": "payload-inspection",
            "label": "Payload inspection"
        },
        {
            "description": "Replay deterministic local events only",
            "id": "bounded-replay",
            "label": "Bounded replay"
        },
        {
            "description": "Reset disposable local state by owner/namespace",
            "id": "namespace-reset",
            "label": "Namespace reset"
        },
        {
            "description": "Export sanitized local reproduction artifacts",
            "id": "report-export",
            "label": "Report export"
        }
    ],
    "positioning": "local-cloud-workflow-debugger",
    "request_id": "local-8fb487557d724178a85c60d1ac1d67d7",
    "safety": {
        "allows_shell_execution": false,
        "bounded_mutations_only": true,
        "local_only": true,
        "uses_real_cloud": false,
        "uses_real_credentials": false
    },
    "service_map": [
        {
            "id": "client",
            "kind": "http-client",
            "label": "Client"
        },
        {
            "id": "api",
            "kind": "lambda-style-handler",
            "label": "API adapter"
        },
        {
            "id": "object-store",
            "kind": "s3-compatible",
            "label": "Object store"
        },
        {
            "id": "metadata-store",
            "kind": "dynamodb-compatible",
            "label": "Metadata store"
        },
        {
            "id": "event-outbox",
            "kind": "local-event-store",
            "label": "Event outbox"
        },
        {
            "id": "processor",
            "kind": "bounded-local-action",
            "label": "Processor"
        }
    ],
    "session": {
        "id": "local-portfolio-evidence",
        "mode": "local",
        "owner_id": "portfolio-evidence",
        "scope": "disposable-emulator-workflow"
    }
}

```

- HTTP status: `200`
- Finished: `2026-06-01T01:39:16Z`


## Create deterministic broken trace

- Started: `2026-06-01T01:39:16Z`
- Request: `POST http://127.0.0.1:8080/ops/demo/broken-trace`

```json
{
    "request_id": "local-4419ea76752a4751a74afec075dfa098",
    "trace": {
        "actions": [
            {
                "id": "inspect-payload",
                "label": "Inspect payload",
                "method": "GET",
                "path": "/ops/traces/trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151",
                "safe": true
            },
            {
                "id": "export-report",
                "label": "Export report",
                "method": "GET",
                "path": "/ops/report?trace_id=trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151",
                "safe": true
            },
            {
                "id": "process-pending",
                "label": "Process pending events",
                "method": "POST",
                "path": "/events/process?limit=10",
                "safe": true
            }
        ],
        "artifact": {
            "event_id": "evt_cbe6d10579324af4bf58d9b73c50a151",
            "event_type": "ObjectCreated",
            "object_id": "obj_8107bc4985a34d58b78020bf9aba617a"
        },
        "commands": [
            {
                "argv": [
                    "curl",
                    "-X",
                    "POST",
                    "-H",
                    "content-type: application/json",
                    "-H",
                    "x-floci-user: portfolio-evidence",
                    "http://127.0.0.1:8080/objects"
                ],
                "command": "curl -X POST -H 'content-type: application/json' -H 'x-floci-user: portfolio-evidence' http://127.0.0.1:8080/objects",
                "kind": "curl",
                "label": "replay object create"
            },
            {
                "argv": [
                    "curl",
                    "-X",
                    "POST",
                    "-H",
                    "x-floci-user: portfolio-evidence",
                    "http://127.0.0.1:8080/events/process?limit=10"
                ],
                "command": "curl -X POST -H 'x-floci-user: portfolio-evidence' 'http://127.0.0.1:8080/events/process?limit=10'",
                "kind": "curl",
                "label": "process pending events"
            }
        ],
        "failure": {
            "code": "processor.validation_failed",
            "reason": "processor rejected payload: missing required metadata customer_id",
            "retryable": true
        },
        "id": "trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151",
        "owner_id": "portfolio-evidence",
        "status": "failed",
        "steps": [
            {
                "detail": "POST /objects accepted by local API adapter",
                "id": "request",
                "label": "API request received",
                "status": "ok"
            },
            {
                "detail": "Content and metadata passed bounded local validation",
                "id": "payload",
                "label": "Payload validated",
                "status": "ok"
            },
            {
                "detail": "objects/portfolio-evidence/obj_8107bc4985a34d58b78020bf9aba617a/broken-order-event.json written to local S3-compatible storage",
                "id": "object-store",
                "label": "Object stored",
                "status": "ok"
            },
            {
                "detail": "DynamoDB-compatible metadata row links owner, category, object id, and key",
                "id": "metadata",
                "label": "Metadata indexed",
                "status": "ok"
            },
            {
                "detail": "evt_cbe6d10579324af4bf58d9b73c50a151 captured as ObjectCreated",
                "id": "outbox",
                "label": "Outbox event emitted",
                "status": "ok"
            },
            {
                "detail": "processor rejected payload: missing required metadata customer_id",
                "id": "processor",
                "label": "Outbox processed",
                "status": "failed"
            }
        ],
        "summary": "request stored object, indexed metadata, emitted event, processor failed with actionable reason"
    }
}

```

- HTTP status: `201`
- Finished: `2026-06-01T01:39:16Z`


## Read broken trace detail

- Started: `2026-06-01T01:39:16Z`
- Request: `GET http://127.0.0.1:8080/ops/traces/trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151`

```json
{
    "request_id": "local-143b6bc0405940eba10a29bd4f87190b",
    "trace": {
        "actions": [
            {
                "id": "inspect-payload",
                "label": "Inspect payload",
                "method": "GET",
                "path": "/ops/traces/trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151",
                "safe": true
            },
            {
                "id": "export-report",
                "label": "Export report",
                "method": "GET",
                "path": "/ops/report?trace_id=trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151",
                "safe": true
            },
            {
                "id": "process-pending",
                "label": "Process pending events",
                "method": "POST",
                "path": "/events/process?limit=10",
                "safe": true
            }
        ],
        "artifact": {
            "event_id": "evt_cbe6d10579324af4bf58d9b73c50a151",
            "event_type": "ObjectCreated",
            "object_id": "obj_8107bc4985a34d58b78020bf9aba617a"
        },
        "commands": [
            {
                "argv": [
                    "curl",
                    "-X",
                    "POST",
                    "-H",
                    "content-type: application/json",
                    "-H",
                    "x-floci-user: portfolio-evidence",
                    "http://127.0.0.1:8080/objects"
                ],
                "command": "curl -X POST -H 'content-type: application/json' -H 'x-floci-user: portfolio-evidence' http://127.0.0.1:8080/objects",
                "kind": "curl",
                "label": "replay object create"
            },
            {
                "argv": [
                    "curl",
                    "-X",
                    "POST",
                    "-H",
                    "x-floci-user: portfolio-evidence",
                    "http://127.0.0.1:8080/events/process?limit=10"
                ],
                "command": "curl -X POST -H 'x-floci-user: portfolio-evidence' 'http://127.0.0.1:8080/events/process?limit=10'",
                "kind": "curl",
                "label": "process pending events"
            }
        ],
        "failure": {
            "code": "processor.validation_failed",
            "reason": "processor rejected payload: missing required metadata customer_id",
            "retryable": true
        },
        "id": "trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151",
        "owner_id": "portfolio-evidence",
        "status": "failed",
        "steps": [
            {
                "detail": "POST /objects accepted by local API adapter",
                "id": "request",
                "label": "API request received",
                "status": "ok"
            },
            {
                "detail": "Content and metadata passed bounded local validation",
                "id": "payload",
                "label": "Payload validated",
                "status": "ok"
            },
            {
                "detail": "objects/portfolio-evidence/obj_8107bc4985a34d58b78020bf9aba617a/broken-order-event.json written to local S3-compatible storage",
                "id": "object-store",
                "label": "Object stored",
                "status": "ok"
            },
            {
                "detail": "DynamoDB-compatible metadata row links owner, category, object id, and key",
                "id": "metadata",
                "label": "Metadata indexed",
                "status": "ok"
            },
            {
                "detail": "evt_cbe6d10579324af4bf58d9b73c50a151 captured as ObjectCreated",
                "id": "outbox",
                "label": "Outbox event emitted",
                "status": "ok"
            },
            {
                "detail": "processor rejected payload: missing required metadata customer_id",
                "id": "processor",
                "label": "Outbox processed",
                "status": "failed"
            }
        ],
        "summary": "request stored object, indexed metadata, emitted event, processor failed with actionable reason"
    }
}

```

- HTTP status: `200`
- Finished: `2026-06-01T01:39:16Z`


## Export sanitized trace report

- Started: `2026-06-01T01:39:16Z`
- Request: `GET http://127.0.0.1:8080/ops/report?trace_id=trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151`

```json
{
    "report": {
        "format": "floci.trace-report.v1",
        "reproduction": {
            "commands": [
                {
                    "argv": [
                        "curl",
                        "-X",
                        "POST",
                        "-H",
                        "content-type: application/json",
                        "-H",
                        "x-floci-user: portfolio-evidence",
                        "http://127.0.0.1:8080/objects"
                    ],
                    "command": "curl -X POST -H 'content-type: application/json' -H 'x-floci-user: portfolio-evidence' http://127.0.0.1:8080/objects",
                    "kind": "curl",
                    "label": "replay object create"
                },
                {
                    "argv": [
                        "curl",
                        "-X",
                        "POST",
                        "-H",
                        "x-floci-user: portfolio-evidence",
                        "http://127.0.0.1:8080/events/process?limit=10"
                    ],
                    "command": "curl -X POST -H 'x-floci-user: portfolio-evidence' 'http://127.0.0.1:8080/events/process?limit=10'",
                    "kind": "curl",
                    "label": "process pending events"
                }
            ],
            "local_only": true,
            "requires_real_cloud": false
        },
        "request_id": "local-66ecd931e2d44f18949b3383b2727254",
        "safety": {
            "allows_shell_execution": false,
            "contains_real_credentials": false,
            "local_only": true,
            "sanitized": true
        },
        "trace": {
            "actions": [
                {
                    "id": "inspect-payload",
                    "label": "Inspect payload",
                    "method": "GET",
                    "path": "/ops/traces/trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151",
                    "safe": true
                },
                {
                    "id": "export-report",
                    "label": "Export report",
                    "method": "GET",
                    "path": "/ops/report?trace_id=trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151",
                    "safe": true
                },
                {
                    "id": "process-pending",
                    "label": "Process pending events",
                    "method": "POST",
                    "path": "/events/process?limit=10",
                    "safe": true
                }
            ],
            "artifact": {
                "event_id": "evt_cbe6d10579324af4bf58d9b73c50a151",
                "event_type": "ObjectCreated",
                "object_id": "obj_8107bc4985a34d58b78020bf9aba617a"
            },
            "commands": [
                {
                    "argv": [
                        "curl",
                        "-X",
                        "POST",
                        "-H",
                        "content-type: application/json",
                        "-H",
                        "x-floci-user: portfolio-evidence",
                        "http://127.0.0.1:8080/objects"
                    ],
                    "command": "curl -X POST -H 'content-type: application/json' -H 'x-floci-user: portfolio-evidence' http://127.0.0.1:8080/objects",
                    "kind": "curl",
                    "label": "replay object create"
                },
                {
                    "argv": [
                        "curl",
                        "-X",
                        "POST",
                        "-H",
                        "x-floci-user: portfolio-evidence",
                        "http://127.0.0.1:8080/events/process?limit=10"
                    ],
                    "command": "curl -X POST -H 'x-floci-user: portfolio-evidence' 'http://127.0.0.1:8080/events/process?limit=10'",
                    "kind": "curl",
                    "label": "process pending events"
                }
            ],
            "failure": {
                "code": "processor.validation_failed",
                "reason": "processor rejected payload: missing required metadata customer_id",
                "retryable": true
            },
            "id": "trace_obj_8107bc4985a34d58b78020bf9aba617a_evt_cbe6d10579324af4bf58d9b73c50a151",
            "owner_id": "portfolio-evidence",
            "status": "failed",
            "steps": [
                {
                    "detail": "POST /objects accepted by local API adapter",
                    "id": "request",
                    "label": "API request received",
                    "status": "ok"
                },
                {
                    "detail": "Content and metadata passed bounded local validation",
                    "id": "payload",
                    "label": "Payload validated",
                    "status": "ok"
                },
                {
                    "detail": "objects/portfolio-evidence/obj_8107bc4985a34d58b78020bf9aba617a/broken-order-event.json written to local S3-compatible storage",
                    "id": "object-store",
                    "label": "Object stored",
                    "status": "ok"
                },
                {
                    "detail": "DynamoDB-compatible metadata row links owner, category, object id, and key",
                    "id": "metadata",
                    "label": "Metadata indexed",
                    "status": "ok"
                },
                {
                    "detail": "evt_cbe6d10579324af4bf58d9b73c50a151 captured as ObjectCreated",
                    "id": "outbox",
                    "label": "Outbox event emitted",
                    "status": "ok"
                },
                {
                    "detail": "processor rejected payload: missing required metadata customer_id",
                    "id": "processor",
                    "label": "Outbox processed",
                    "status": "failed"
                }
            ],
            "summary": "request stored object, indexed metadata, emitted event, processor failed with actionable reason"
        }
    },
    "request_id": "local-66ecd931e2d44f18949b3383b2727254"
}

```

- HTTP status: `200`
- Finished: `2026-06-01T01:39:16Z`


## Reviewer notes

- If all endpoint statuses are 200/201, the first-click debugger path is runtime-verified.
- If demo endpoints return 503 `local_dependency_unavailable`, the API is still behaving correctly for missing local emulator resources; do not auto-run Terraform apply without approval.
- This file is safe to include in a portfolio review because it contains only local emulator evidence and sanitized output.
