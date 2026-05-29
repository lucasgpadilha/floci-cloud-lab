# Floci Studio Foundation Architecture

Status: implemented foundation slice
Date: 2026-05-28

## Goal

Make Floci Studio extensible around the durable product wedge: local cloud workflow debugging.

The foundation intentionally separates:

1. HTTP adapter concerns (`api.py`)
2. Product/session contract (`ops/session.py`)
3. Trace normalization and causal timeline building (`ops/traces.py`)
4. Sanitized report export (`ops/reports.py`)
5. Storage/event persistence (`repository.py`, `events.py`, `storage.py`)

This keeps the API from becoming a monolithic dashboard backend and lets future adapters implement the same contracts.

## Module boundaries

### `app/backend/functions/api.py`

Owns only HTTP/Lambda-style concerns:

- method/path routing;
- request parsing;
- validation;
- response envelope;
- observability emission;
- repository dependency injection.

It should not know UI layout or dashboard card concepts.

### `app/backend/functions/ops/session.py`

Builds the stable session/capability contract consumed by Studio clients.

Key rule: describe safe local debugging capabilities, not fake cloud-console status.

### `app/backend/functions/ops/traces.py`

Normalizes raw repository events into product-level trace models.

Core model:

`TraceEvent -> trace summary -> trace detail -> causal steps + reproduction commands`

This is the strategic differentiator. New services should extend trace steps and artifacts here instead of leaking resource-specific logic into the UI.

### `app/backend/functions/ops/reports.py`

Exports sanitized, portfolio-ready trace reports.

Reports must remain:

- local-only;
- secret-safe;
- reproducible;
- useful as bug reports / OSS evidence / interview artifacts.

## Current endpoint foundation

- `GET /ops/session`
- `GET /ops/traces?limit=&status=`
- `GET /ops/traces/{trace_id}`
- `GET /ops/report?trace_id=`
- `POST /ops/demo/trace`

## Expansion pattern

When adding a new workflow service, use this order:

1. Add repository/event shape if persistence is needed.
2. Add a `TraceEvent` normalization test.
3. Add trace step/artifact expectations.
4. Add API endpoint test only after the product model test exists.
5. Keep UI derived from trace/session contracts, not bespoke dashboard JSON.

## Anti-slop gates

A new endpoint or UI field must answer at least one:

- What happened?
- Where did it happen?
- Which payload/artifact caused it?
- What is the local resource involved?
- How do I reproduce or replay it?
- How do I export safe evidence?

If it only exists to make the screen look busy, reject it.

## Tests

Foundation tests:

- `tests/unit/test_ops_foundation.py`
- `tests/unit/test_api_handler.py` ops endpoint coverage

Current verification:

`88 passed`
