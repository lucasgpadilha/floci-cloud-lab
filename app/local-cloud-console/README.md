# Floci Studio — Local Workflow Debugger

Floci Studio is no longer framed as a generic local cloud dashboard. This incubator is the browser workbench for debugging cloud-shaped workflows that run fully on the local Floci emulator.

## Goal

Answer the professional debugging questions first:

- What request started the flow?
- Which local object/event artifacts were created?
- Which processor step failed?
- What exact reason caused the failure?
- Can we export sanitized, local-only evidence for review?

The first reference flow is the broken trace demo backed by `POST /ops/demo/broken-trace`.

## Quickstart

1. Start Floci and the local API from the repo root:

```bash
make floci-up
make app-api-local
```

2. Open Floci Studio:

```bash
# Option A: open directly in your browser
app/local-cloud-console/index.html

# Option B: serve statically from this folder
python3 -m http.server 5174 -d app/local-cloud-console
```

3. Use defaults:

- API URL: `http://127.0.0.1:8080`
- Owner: `browser-demo`

4. Click `Create broken trace`.

Expected result: a failed local processor trace with failure code `processor.validation_failed`, causal steps, reproduction commands, and a sanitized report export.

## Product principles

- Debugger first, dashboard second.
- Trace is the primary object.
- Causal flow beats resource inventory.
- Local-only safety is explicit.
- Browser never executes shell commands.
- Reports are sanitized before export.

## Main endpoints

- `POST /ops/demo/broken-trace`
- `GET /ops/traces?status=failed&limit=10`
- `GET /ops/traces/{trace_id}`
- `GET /ops/report?trace_id={trace_id}`
- `GET /objects/{object_id}` for supporting object evidence

## Safety boundary

- No real AWS.
- No real credentials.
- Local endpoint guard blocks non-local API URLs.
- Commands are displayed for copy/review only.
- Reports surface `sanitized`, `local_only`, `uses_real_cloud`, and `allows_shell_execution` flags.

## API contract

See:

`docs/contracts/local-cloud-console-api.md`

## Extraction note

This folder remains an incubator, but the extraction target is now sharper than “local cloud console”: a reusable local workflow debugger for emulator-backed cloud labs. Future adapters can target Floci, LocalStack, MinIO, DynamoDB Local, or Testcontainers-backed labs as long as they implement the trace/report contract.
