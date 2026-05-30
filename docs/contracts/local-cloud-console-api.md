# Floci Studio Local Workflow API Contract

This contract defines the HTTP boundary between Floci Studio and a local cloud-emulator adapter. The first adapter is Floci Cloud Lab. The contract is trace/debugger-first: UI clients should build around sessions, traces, reports, and bounded local actions rather than generic dashboard metrics.

## Safety and scope

- Default base URL: `http://127.0.0.1:8080`
- Default owner header: `x-floci-user: browser-demo`
- Local-only by design: localhost / 127.0.0.1 endpoints only.
- No real AWS credentials are required or stored.
- No browser-triggered arbitrary shell execution is allowed.
- Mutations must be explicit and bounded.
- The dashboard may visualize AWS-equivalent resource types, but responses represent local emulator resources.

## Common response fields

Every successful JSON response should include:

```json
{
  "request_id": "local-or-client-request-id"
}
```

Errors follow the existing API shape:

```json
{
  "error": { "code": "validation_error", "message": "human readable message" },
  "request_id": "..."
}
```

## Required endpoints

### `GET /health`

Returns API liveness.

```json
{
  "ok": true,
  "service": "floci-cloud-lab-api",
  "runtime": "local-floci",
  "version": "0.1.0",
  "request_id": "..."
}
```

### `GET /ops/status`

Returns console-level status, component capabilities, and safety flags. This endpoint is deterministic and does not shell out.

```json
{
  "status": "ready",
  "mode": "local",
  "service": "floci-cloud-lab-api",
  "runtime": "local-floci",
  "environment": {
    "local_only": true,
    "cloud_provider": "aws-compatible",
    "emulator": "floci",
    "region": "us-east-1",
    "account_id": "000000000000"
  },
  "emulator": {
    "name": "Floci",
    "endpoint": "http://localhost:4566",
    "connected": true,
    "status": "online"
  },
  "database": { "engine": "DynamoDB (Local)", "status": "online" },
  "storage": { "engine": "S3 (Local)", "status": "online" },
  "components": [
    {
      "id": "api",
      "name": "Backend API",
      "category": "compute",
      "status": "online",
      "engine": "Python Lambda-style HTTP adapter",
      "aws_equivalent": "AWS::Lambda::Function",
      "capabilities": ["http-api", "object-crud", "event-processing", "cors"]
    }
  ],
  "safety": {
    "local_only": true,
    "uses_real_cloud": false,
    "uses_real_credentials": false,
    "allows_shell_execution": false,
    "bounded_mutations_only": true
  },
  "dashboard": {
    "recommended_refresh_seconds": 5,
    "primary_actions": [
      { "id": "create-demo-object", "label": "Create demo object", "method": "POST", "path": "/objects", "safe": true },
      { "id": "process-events", "label": "Process pending events", "method": "POST", "path": "/events/process?limit=10", "safe": true }
    ]
  },
  "request_id": "..."
}
```

### `GET /ops/resources`

Returns local resources and AWS-equivalent mappings.

```json
{
  "resources": [
    {
      "id": "objects-bucket",
      "name": "floci-cloud-lab-local-objects",
      "type": "AWS::S3::Bucket",
      "category": "storage",
      "local_id": "local-objects-bucket",
      "aws_equivalent": {
        "service": "s3",
        "resource_type": "bucket",
        "cloudformation_type": "AWS::S3::Bucket"
      },
      "status": "available",
      "description": "Primary object storage",
      "capabilities": ["put-object", "get-object", "list-objects", "versioning"],
      "safety": { "local_only": true, "contains_demo_data": true, "uses_real_cloud": false, "allows_shell_execution": false },
      "dashboard": { "display_order": 10, "badge": "Storage", "recommended_view": "resource-card" }
    }
  ],
  "categories": [
    { "id": "compute", "label": "Compute", "description": "Local API and request handling" },
    { "id": "storage", "label": "Storage", "description": "S3-compatible object storage" },
    { "id": "database", "label": "Database", "description": "DynamoDB-compatible metadata and events" },
    { "id": "observability", "label": "Observability", "description": "Logs, metrics, and traces" }
  ],
  "summary": { "count": 4, "available": 4, "degraded": 0, "offline": 0, "local_only": true },
  "request_id": "..."
}
```

### `GET /ops/session`

Returns the product-level debugging session contract. This is the preferred endpoint for Studio-style clients because it describes adapter identity, safe capabilities, and the canonical service map without pretending to be a full AWS Console.

```json
{
  "session": { "id": "local-browser-demo", "owner_id": "browser-demo", "mode": "local", "scope": "disposable-emulator-workflow" },
  "positioning": "local-cloud-workflow-debugger",
  "adapter": { "name": "floci", "endpoint": "http://localhost:4566", "runtime": "aws-compatible-local-emulator" },
  "safety": { "local_only": true, "uses_real_cloud": false, "uses_real_credentials": false, "allows_shell_execution": false, "bounded_mutations_only": true },
  "capabilities": [
    { "id": "flow-traces", "label": "Flow traces" },
    { "id": "payload-inspection", "label": "Payload inspection" },
    { "id": "bounded-replay", "label": "Bounded replay" },
    { "id": "namespace-reset", "label": "Namespace reset" },
    { "id": "report-export", "label": "Report export" }
  ],
  "service_map": [
    { "id": "client", "label": "Client", "kind": "http-client" },
    { "id": "api", "label": "API adapter", "kind": "lambda-style-handler" },
    { "id": "object-store", "label": "Object store", "kind": "s3-compatible" },
    { "id": "metadata-store", "label": "Metadata store", "kind": "dynamodb-compatible" },
    { "id": "event-outbox", "label": "Event outbox", "kind": "local-event-store" },
    { "id": "processor", "label": "Processor", "kind": "bounded-local-action" }
  ],
  "request_id": "..."
}
```

### `GET /ops/traces?limit={limit}&status={status}`

Returns recent workflow trace summaries derived from local object/outbox events.

```json
{
  "data": {
    "count": 1,
    "traces": [
      {
        "id": "trace_obj_..._evt_...",
        "owner_id": "browser-demo",
        "status": "pending",
        "method": "POST",
        "path": "/objects",
        "summary": "request stored object, indexed metadata, emitted event, awaiting processor",
        "artifact": { "object_id": "obj_...", "event_id": "evt_...", "event_type": "ObjectCreated" },
        "links": { "detail": "/ops/traces/trace_obj_..._evt_..." }
      }
    ]
  },
  "request_id": "..."
}
```

### `GET /ops/traces/{trace_id}`

Returns a causal trace detail with steps and copyable commands.

```json
{
  "trace": {
    "id": "trace_obj_..._evt_...",
    "status": "pending",
    "steps": [
      { "id": "request", "label": "API request received", "status": "ok" },
      { "id": "payload", "label": "Payload validated", "status": "ok" },
      { "id": "object-store", "label": "Object stored", "status": "ok" },
      { "id": "metadata", "label": "Metadata indexed", "status": "ok" },
      { "id": "outbox", "label": "Outbox event emitted", "status": "ok" },
      { "id": "processor", "label": "Outbox processed", "status": "waiting" }
    ],
    "commands": [
      { "label": "replay object create", "command": "curl ... /objects" },
      { "label": "process pending events", "command": "curl ... /events/process?limit=10" }
    ]
  },
  "request_id": "..."
}
```

### `GET /ops/report?trace_id={trace_id}`

Exports a sanitized portfolio-ready trace report. If `trace_id` is omitted, the most recent trace is used.

```json
{
  "report": {
    "format": "floci.trace-report.v1",
    "trace": { "id": "trace_obj_..._evt_...", "status": "pending", "steps": [] },
    "safety": { "sanitized": true, "contains_real_credentials": false, "local_only": true, "allows_shell_execution": false },
    "reproduction": { "local_only": true, "requires_real_cloud": false, "commands": [] }
  },
  "request_id": "..."
}
```

### `POST /ops/demo/trace`

Creates a deterministic bounded local flow for demos and returns the complete trace. This endpoint is safe only because it uses local demo data, local-only storage, and the existing bounded event processor.

### `POST /ops/demo/broken-trace`

Creates a deterministic local flow that fails at the processor step. This is the preferred demo for proving the Studio debugger wedge because it returns a reportable trace with an actionable failure reason.

```json
{
  "trace": {
    "id": "trace_obj_..._evt_...",
    "status": "failed",
    "failure": {
      "code": "processor.validation_failed",
      "reason": "processor rejected payload: missing required metadata customer_id",
      "retryable": true
    },
    "steps": [
      { "id": "request", "status": "ok" },
      { "id": "payload", "status": "ok" },
      { "id": "object-store", "status": "ok" },
      { "id": "metadata", "status": "ok" },
      { "id": "outbox", "status": "ok" },
      { "id": "processor", "status": "failed" }
    ],
    "actions": [
      { "id": "inspect-payload", "safe": true },
      { "id": "export-report", "safe": true },
      { "id": "process-pending", "safe": true }
    ]
  },
  "request_id": "..."
}
```

### `GET /objects?limit={limit}&cursor={cursor}&category={category}`

Lists local object metadata for the active owner.

```json
{
  "data": {
    "count": 1,
    "objects": [
      {
        "object_id": "obj_...",
        "owner_id": "browser-demo",
        "name": "demo.md",
        "category": "console-demo",
        "content_type": "text/markdown",
        "size_bytes": 128,
        "s3_bucket": "floci-cloud-lab-local-objects",
        "s3_key": "objects/browser-demo/obj_.../demo.md",
        "sha256": "...",
        "metadata": { "source": "local-cloud-console" }
      }
    ],
    "next_cursor": null
  },
  "request_id": "..."
}
```

### `POST /objects`

Creates a bounded local demo object. The dashboard uses this for “Create demo object”.

```json
{
  "name": "console-demo.md",
  "content": "# demo",
  "content_type": "text/markdown",
  "metadata": { "category": "console-demo", "source": "local-cloud-console" }
}
```

### `GET /objects/{object_id}`

Returns object detail, including content preview where available.

### `GET /events?limit={limit}&status={status}`

Lists local outbox events for the active owner.

### `POST /events/process?limit={limit}`

Processes a bounded number of local pending events. This is safe for local demos only and must not shell out.

## Future optional endpoints

- `GET /ops/evidence` — curated evidence payload and copyable commands.
- `POST /ops/demo/object` — deterministic demo-object wrapper over `POST /objects`.
- `GET /ops/logs` — lightweight local log view if exposed safely.

## Adapter extraction notes

A future standalone `local-cloud-console` repo should treat this as the first adapter contract. Other adapters, such as LocalStack or MinIO, can implement the same endpoints while keeping the UI unchanged.
