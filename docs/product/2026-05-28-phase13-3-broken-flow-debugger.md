# Phase 13.3 — Broken Flow Debugger

Status: implemented first vertical slice
Date: 2026-05-28

## Purpose

Prove Floci Studio's core differentiator with a deliberately broken local workflow.

The goal is not to show another dashboard state. The goal is to answer:

- What request started the flow?
- Which local object/event was created?
- Which processor step failed?
- What exact reason caused the failure?
- Can the failure be exported as safe evidence?

## Endpoint

### `POST /ops/demo/broken-trace`

Creates a deterministic local object/event flow and marks the processor step failed with an actionable reason.

Returned trace shape:

- `status: failed`
- `failure.code: processor.validation_failed`
- causal steps ending in failed `processor`
- safe actions:
  - inspect payload
  - export report
  - process pending events

## Failure scenario

The demo object is an order-like JSON payload:

```json
{"order_id":"demo-1001","total":42}
```

The local processor expects `customer_id` metadata. The demo intentionally omits it, producing:

```text
processor rejected payload: missing required metadata customer_id
```

## Why this matters

This is the first product-level proof that Floci Studio is not competing as a generic resource console. It shows a local cloud-shaped flow as a causal debugging artifact.

## Expansion path

Next slices should add:

1. trace replay that creates a corrected payload;
2. namespace reset scoped to the demo owner;
3. UI binding for failed flow inspection;
4. report download/copy workflow;
5. more failure adapters: invalid schema, DLQ-like retry exhaustion, missing object, metadata conflict.
