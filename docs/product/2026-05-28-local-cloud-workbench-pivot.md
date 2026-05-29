# Local Cloud Workbench Pivot — Anti AI-Slop Product Direction

> Status: product pivot proposal for Phase 13.2. This replaces the generic “local cloud dashboard” direction with a trace-first local debugging workbench.

## Brutal diagnosis

The current console implementation is useful as an incubator, but it still risks being perceived as AI slop because it copies the visual grammar of a SaaS/cloud dashboard before earning the product semantics.

The weak pattern is:

- sidebar;
- KPI cards;
- resource cards;
- generic tables;
- “evidence JSON”;
- AWS-ish labels;
- all-green status;
- little causal debugging depth.

That looks like a dashboard generated from nouns, not a product designed from developer jobs.

## Product wedge

Build **Local Cloud Workbench**, not an AWS-console clone.

One-sentence positioning:

> A lightweight local-first trace/debug workbench for cloud-shaped emulator workflows: inspect what happened, why it happened, what broke, and export a reproducible local run report — no real cloud credentials, no browser shell execution.

## Inspirations researched

Use these as pattern references, not clones:

- **Inngest Dev Server** — event/function/run/step inspection; replay and causality.
- **Temporal UI** — execution history seriousness and failure visibility.
- **Supabase Studio** — concrete backend tools, not abstract dashboards.
- **Vercel Dashboard** — artifact/session detail polish and clear run history.
- **SST Console/Ion** — app/resource relationship and developer-first infra UX.
- **Convex Dashboard** — code/data/logs connected to programming model.
- **Sentry** — issue/event detail with linked logs and context.
- **Datadog/Grafana** — correlation patterns only; avoid fake charts.
- **Linear/Raycast** — restrained high-quality interaction and command speed.

## What to avoid

- KPI-first dashboard.
- AWS Console cosplay.
- Generic “Resources / Analytics / Reports” navigation.
- Decorative charts without real time-series data.
- Glassmorphism/AI-purple-gradient aesthetic.
- Cards that only document nouns instead of enabling actions.
- Fake business metrics.
- Browser terminal or arbitrary shell execution.
- Real AWS credentials or hosted cloud assumptions.

## New core object model

The product should organize around local runtime facts:

### Lab Session

A single local run/environment.

Fields:

- session id;
- adapter name/version;
- local endpoint;
- started_at;
- status;
- services;
- capabilities;
- safety flags;
- health checks.

### Trace

A correlated workflow caused by a request/action/event.

Fields:

- trace_id/request_id;
- owner;
- action;
- status;
- started_at/completed_at;
- duration_ms;
- steps;
- linked object ids;
- linked event ids;
- errors;
- copyable repro.

### Trace Step

A causal state transition.

Examples:

1. API request received.
2. Payload validated.
3. Object stored.
4. Metadata indexed.
5. Outbox event emitted.
6. Event processor attempted.
7. Processor result recorded.

Each step has:

- status;
- timestamp;
- component;
- payload/ref;
- logs;
- error message when relevant.

### Capability

Adapter-declared feature availability.

Examples:

- object_store;
- metadata_store;
- event_outbox;
- event_replay;
- logs;
- topology;
- reset_namespace;
- export_report.

The UI renders capabilities, not hardcoded AWS service panels.

## Proposed navigation

Keep it shallow and job-driven:

1. **Workbench** — active lab session + recent traces.
2. **Topology** — local graph: app/API → object store → metadata → outbox → processor.
3. **Traces** — request/event workflow history.
4. **Data** — object and metadata inspector.
5. **Events** — outbox with pending/processed/failed and safe processing.
6. **Logs** — filtered structured logs, later.
7. **Report** — export reproducible session/report artifact.

## Hero screen redesign

The hero screen should not start with KPI cards. It should start with:

- active lab session status;
- topology strip/map;
- recent traces list;
- selected trace detail/timeline;
- safe action bar.

Recommended layout:

```text
┌────────────────────────────────────────────────────────────────────┐
│ Local Cloud Workbench    Floci adapter · local · safe              │
├───────────────┬──────────────────────────────┬─────────────────────┤
│ Sidebar       │ Recent traces                │ Selected trace       │
│ Workbench     │                              │ timeline             │
│ Topology      │ POST /objects   processed    │ 1 request received   │
│ Traces        │ POST /events    failed       │ 2 object stored      │
│ Data          │ GET /objects    ok           │ 3 metadata indexed   │
│ Events        │                              │ 4 event pending      │
│ Report        │                              │ payload/logs/actions │
├───────────────┴──────────────────────────────┴─────────────────────┤
│ Topology: Browser → API → Object Store → Metadata → Outbox → Worker│
└────────────────────────────────────────────────────────────────────┘
```

## Signature feature

The braba is not “pretty dashboard”.

The signature feature should be:

> Click any local workflow and see the complete causal trace across request, object storage, metadata, event outbox, processing, logs, and exportable repro.

That gives the project a differentiated product reason to exist.

## API changes for Phase 13.2

Add adapter capability and trace endpoints.

### `GET /ops/session`

Returns active lab session and capabilities.

### `GET /ops/traces?limit=25&status=&owner=`

Returns recent workflow traces. For the current Floci lab, traces can initially be synthesized from object metadata and event records by request_id/object_id.

### `GET /ops/traces/{trace_id}`

Returns full timeline:

- request received;
- object written;
- metadata written;
- event emitted;
- processing attempts.

### `POST /ops/demo/trace`

Creates a deterministic demo workflow and returns the trace id. This wraps `POST /objects` and optionally processes one event. It is bounded and local-only.

### `GET /ops/report?trace_id=`

Returns sanitized Markdown/JSON report for a trace or session.

## UI implementation direction

Stop evolving the current dashboard as-is. Replace it with one of these:

### Preferred: Trace Workbench

- Dense three-pane layout.
- Recent traces table/list in center.
- Inspector timeline on right.
- Topology as a compact persistent strip.
- Actions tied to selected trace.

### Secondary: Local Observability Mini-console

- Live event/log stream.
- Filters by owner/status/component.
- Request/event detail drawer.
- Minimal real charts only when real data exists.

### Later: Command Console

- Raycast-style command palette.
- Search resources, traces, actions.
- Power-user accelerator, not MVP foundation.

## Visual rules

- Neutral palette: zinc/slate/neutral.
- One accent color only.
- Semantic colors only for status.
- Monospace for IDs, paths, endpoints, logs, payloads.
- Tables/split panes over big cards.
- Timeline over KPI grid.
- Topology over fake charts.
- Empty states that teach exact commands/URLs.
- Every panel must answer one of:
  - What happened?
  - Where is the data?
  - Why did it fail?
  - What can I safely do next?
  - How do I reproduce/share this?

## Phase 13.2 acceptance criteria

A user can:

1. Open the workbench locally.
2. See adapter/session/capability status.
3. Create one deterministic demo trace.
4. See the trace appear in recent traces.
5. Click the trace.
6. Inspect a timeline with at least 5 causal steps.
7. See object id, S3 key, metadata, event id/status, and processing attempts linked together.
8. Process/retry bounded local events from a safe action.
9. Export a sanitized run report.
10. Verify no real cloud credentials, no arbitrary shell execution, and no non-local endpoint by default.

## Implementation plan

### Task 1 — Add trace model tests

Modify:

- `tests/unit/test_api_handler.py`

Add tests for:

- `GET /ops/session`;
- `POST /ops/demo/trace`;
- `GET /ops/traces`;
- `GET /ops/traces/{trace_id}`;
- `GET /ops/report?trace_id=...`.

### Task 2 — Implement trace/session endpoints

Modify:

- `app/backend/functions/api.py`

Keep implementation local and deterministic. Reuse repository methods already available. If a full trace store does not exist yet, synthesize traces from object/event records.

### Task 3 — Replace dashboard with workbench UI

Modify:

- `app/local-cloud-console/index.html`

Replace KPI/card-first UI with:

- session header;
- topology strip;
- recent traces list;
- selected trace timeline;
- data/event inspector tabs;
- report export.

### Task 4 — Rename docs language

Modify:

- `app/local-cloud-console/README.md`
- `docs/contracts/local-cloud-console-api.md`

Use “workbench”, “trace”, “adapter”, and “local session” language. Keep AWS mappings secondary.

### Task 5 — Safety and smoke tests

Add/extend tests to assert:

- no `innerHTML` for API payload rendering;
- no real AWS credential strings;
- no shell execution strings;
- non-local API URL is blocked in the browser code;
- all mutating endpoints are bounded and local-only.

## Name direction

Best names:

1. **Local Cloud Workbench** — broad, serious, OSS-friendly.
2. **Cloud Emulator Inspector** — sharper and descriptive.
3. **Local Cloud Trace Console** — most aligned with the wedge.

Recommendation:

Use **Local Cloud Workbench** as product name, with trace-first positioning in the tagline.

Tagline:

> Trace, debug, and report local cloud emulator workflows without touching real cloud.

## Decision

Do not polish the current dashboard further as a generic cloud console.

Pivot Phase 13.2 to a trace-first workbench. The current commit can remain as a stepping stone, but it should not be the product direction.
