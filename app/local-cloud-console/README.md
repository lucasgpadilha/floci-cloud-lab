# Local Cloud Console Dashboard

Reusable incubator slice for a lightweight, open-source-ready Local Cloud Console inside Floci Cloud Lab.

## Goal

Visualize local cloud-emulator systems with a console-quality UI without becoming heavy like a full cloud provider console. The first adapter is Floci Cloud Lab; future adapters can target LocalStack, MinIO, DynamoDB Local, or Testcontainers-backed labs.

## Quickstart

1. Start Floci and the local API from the repo root:

```bash
make floci-up
make app-api-local
```

2. Open the dashboard:

```bash
# Option A: open directly in your browser
app/local-cloud-console/index.html

# Option B: serve statically from this folder
python3 -m http.server 5174 -d app/local-cloud-console
```

3. Use defaults:

- API URL: `http://127.0.0.1:8080`
- Owner: `browser-demo`

## Features

- Local-only badge and endpoint guard.
- API/emulator/resource/object/event KPIs.
- Resource cards with AWS-equivalent mappings.
- Object explorer with category filter and object detail drawer.
- Event outbox viewer with status filter.
- Safe bounded actions:
  - create demo object through `POST /objects`
  - process local pending events through `POST /events/process?limit=10`
- JSON evidence panel with copy button.
- No browser shell execution.
- No real AWS credentials.

## API contract

See:

`docs/contracts/local-cloud-console-api.md`

## Open-source extraction note

This folder is intentionally an incubator. Once the adapter contract stabilizes, extract it into a standalone repository such as `local-cloud-console` and keep Floci Cloud Lab as the first reference adapter/demo.

Before extraction, keep these constraints:

- No dependency on Floci internals beyond HTTP responses.
- No real cloud account assumptions.
- No hosted CI requirement.
- No static real credentials.
- No arbitrary shell execution from the browser.
