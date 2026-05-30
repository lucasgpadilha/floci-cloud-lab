# Local Cloud Workbench OSS Incubation Plan

> Status: revised after the anti-AI-slop product pivot. This supersedes the old “Local Cloud Console Dashboard” direction.

## Product decision

Do not keep polishing a generic cloud dashboard.

The product direction is now **Local Cloud Workbench**: a trace-first local debugging workbench for cloud-shaped emulator workflows.

Tagline:

> Trace, debug, and report local cloud emulator workflows without touching real cloud.

The Floci Cloud Lab remains the portfolio/lab. The workbench is the productizable OSS candidate incubated inside the lab until its adapter contract and trace model are stable.

## Why the pivot matters

The previous dashboard direction risked looking like AI slop because it was organized around generic dashboard nouns:

- sidebar;
- KPI cards;
- resource cards;
- generic tables;
- evidence JSON panel;
- AWS-console cosplay;
- all-green status with little causal debugging depth.

A serious developer tool should start from the user's actual job:

- What happened in this local workflow?
- Where did the data go?
- Which local resource was touched?
- Which event was emitted?
- What processed it?
- Where did it fail?
- How do I reproduce it?
- How do I export a safe report?

## Product wedge

The signature feature is:

> Click any local workflow and see the complete causal trace across request, validation, object storage, metadata indexing, event outbox, processing, logs, and an exportable sanitized repro/report.

This makes the workbench compete more with devtool/debugging patterns than with a cloud console clone:

- Inngest Dev Server: event/function run inspection;
- Temporal UI: execution history and failure visibility;
- Supabase Studio: concrete backend tools;
- Sentry: event detail and debugging context;
- Vercel: run/session artifact polish;
- Linear/Raycast: restrained, fast, serious interaction.

Use these as pattern references, not visual clones.

## Non-goals

- Do not build an AWS Console clone.
- Do not build fake KPI dashboards.
- Do not add decorative charts without real time-series data.
- Do not expose arbitrary shell execution from the browser.
- Do not require real AWS credentials.
- Do not add GitHub Actions/GitLab runner config.
- Do not create/mutate real cloud resources.
- Do not split into a separate repo before the adapter contract is stable.

## Core object model

### Lab Session

Represents the active local runtime/environment.

Required fields:

- session_id;
- adapter name/version;
- endpoint;
- region/account placeholder;
- started_at;
- status;
- capabilities;
- safety flags;
- service map/topology.

### Trace

Represents a correlated local workflow triggered by a request/action/event.

Required fields:

- trace_id or request_id;
- owner/namespace;
- action;
- status;
- started_at/completed_at;
- duration_ms when available;
- linked object ids;
- linked event ids;
- errors;
- copyable repro commands.

### Trace Step

Represents one causal transition.

Examples:

1. API request received.
2. Payload validated.
3. Object stored in S3-compatible local store.
4. Metadata indexed in DynamoDB-compatible local table.
5. Outbox event emitted.
6. Processor attempted.
7. Processor result recorded.
8. Report exported.

Each step should expose:

- timestamp;
- component;
- status;
- reference/payload summary;
- log/error details when safe;
- links to related resources.

### Capability

Adapter-declared feature support. The UI renders capabilities instead of hardcoding AWS service panels.

Examples:

- flow_traces;
- payload_inspection;
- object_store;
- metadata_store;
- event_outbox;
- bounded_replay;
- report_export;
- topology;
- local_dependency_health.

## Adapter/API contract

Minimum Phase 13.2 contract:

### `GET /ops/session`

Returns the active lab session, adapter metadata, capabilities, service map, and safety flags.

Must prove:

- local_only: true;
- uses_real_cloud: false;
- uses_real_credentials: false;
- allows_shell_execution: false;
- bounded_mutations_only: true.

### `GET /ops/traces?limit=25&status=&owner=`

Returns recent local workflow traces.

For Floci Cloud Lab, traces may initially be synthesized from object metadata and outbox event records.

### `GET /ops/traces/{trace_id}`

Returns a full causal timeline for a trace.

### `POST /ops/demo/trace`

Creates one deterministic bounded local demo workflow and returns a trace id.

Rules:

- no arbitrary command execution;
- no real cloud endpoint;
- no unbounded loops;
- deterministic owner/category/name;
- useful failure payloads if local bucket/table are missing.

### `POST /ops/demo/broken-trace`

Creates or simulates a controlled failing workflow so the workbench demonstrates debugging, not only happy-path green states.

### `GET /ops/report?trace_id=...`

Returns a sanitized Markdown/JSON report for a trace or session.

Must redact secret-like values such as access keys, secret keys, tokens, passwords, API keys, and credentials.

## UI architecture

Replace KPI/card-first layout with a trace-first workbench.

Recommended first screen:

```text
┌────────────────────────────────────────────────────────────────────┐
│ Local Cloud Workbench    Floci adapter · local · safe              │
├───────────────┬──────────────────────────────┬─────────────────────┤
│ Session       │ Recent traces                │ Selected trace       │
│ Capabilities  │                              │ timeline             │
│ Safety        │ POST /objects   processed    │ 1 request received   │
│ Topology      │ POST /events    failed       │ 2 payload validated  │
│ Report        │ GET /objects    ok           │ 3 object stored      │
│               │                              │ 4 event emitted      │
│               │                              │ payload/logs/repro   │
├───────────────┴──────────────────────────────┴─────────────────────┤
│ Topology: Browser → API → Object Store → Metadata → Outbox → Worker│
└────────────────────────────────────────────────────────────────────┘
```

Visual rules:

- neutral palette, one accent color;
- semantic colors only for status;
- monospace for IDs, paths, endpoints, logs, and payloads;
- split panes and timelines over giant cards;
- topology over fake charts;
- copyable repro/report controls;
- empty states that teach exact local commands;
- no glassmorphism or AI-purple-gradient aesthetic.

## Phase 13.2 implementation tasks

### Task 1 — Verify existing Phase 13 branch

Branch/worktree:

- `/home/lucas/agentic/runs/floci-cloud-lab-gemini-phase13`
- `phase13-local-cloud-console-gemini`

Run:

```bash
make check
.venv/bin/python -m pytest tests/unit/test_ops_foundation.py tests/unit/test_local_cloud_console_static.py tests/unit/test_api_handler.py -q
make floci-up
make floci-health
```

Runtime probe:

```bash
GET  http://127.0.0.1:8080/health
GET  http://127.0.0.1:8080/ops/session
GET  http://127.0.0.1:8080/ops/traces?limit=5
POST http://127.0.0.1:8080/ops/demo/trace
GET  http://127.0.0.1:8080/ops/report?trace_id=...
```

If local bucket/table are missing, the product must return actionable HTTP 503 `local_dependency_unavailable`, not a generic 500. Do not run Terraform apply without explicit approval.

### Task 2 — Close API gaps

Ensure these endpoints exist and have unit tests:

- `GET /ops/session`;
- `GET /ops/traces`;
- `GET /ops/traces/{trace_id}`;
- `POST /ops/demo/trace`;
- `POST /ops/demo/broken-trace`;
- `GET /ops/report`.

### Task 3 — Replace dashboard semantics

Update `app/local-cloud-console/index.html` so it presents a workbench, not a dashboard.

Required sections:

- active session header;
- safety/capability strip;
- recent traces list;
- selected trace timeline;
- topology strip;
- payload/log/repro inspector;
- export sanitized report action;
- controlled failing workflow demo.

### Task 4 — Safety/static tests

Tests must assert:

- no arbitrary shell execution strings;
- no browser use of `eval`;
- no raw API payload rendering with unsafe `innerHTML`;
- non-local API URLs are rejected by default;
- secret-like strings are redacted from reports;
- mutation actions are bounded and explicit.

### Task 5 — Evidence and docs

Add/update:

- product pivot doc;
- adapter contract doc;
- README quickstart;
- evidence showing success trace and broken trace;
- screenshots or reproducible local serve instructions.

## OSS extraction strategy

Do not create a new GitHub repository yet.

Incubate inside Floci Cloud Lab until:

- the workbench opens locally with one command;
- trace endpoints are stable;
- success and failure traces are demonstrable;
- report export is sanitized;
- README is good enough for a stranger;
- Floci-specific assumptions are isolated behind adapter/config language;
- safety tests pass;
- there is real evidence/screenshots.

Then extract as a separate OSS project.

Recommended product name:

- Local Cloud Workbench

Alternative names:

- Cloud Emulator Inspector
- Local Cloud Trace Console

## Acceptance criteria for the braba

A reviewer can:

1. Open the workbench locally.
2. See that it is local-only and safe.
3. Create a deterministic successful trace.
4. Create or load a controlled failing trace.
5. Click a trace and inspect at least five causal steps.
6. See object id, S3 key, metadata, event id/status, and processing attempts linked together.
7. Export a sanitized trace/session report.
8. Understand exactly how this maps to real AWS concepts without believing real AWS was touched.
9. Verify no shell execution, no real credentials, and no hosted CI runner config.
10. Explain the product wedge in one sentence.

## Current known validation notes

From the latest audit:

- `make check` passed in the Phase 13 worktree.
- Targeted ops/static/API tests pass when using the repo venv.
- `python3 -m pytest ...` without the venv may fail if botocore is not installed globally; use `.venv/bin/python` or `make check`.
- `make floci-up` and `make floci-health` are safe local emulator checks and passed.
- Runtime `/ops/session` responds without needing local bucket/table.
- Runtime `/ops/traces`, `/ops/report`, and `/ops/demo/trace` correctly return actionable `local_dependency_unavailable` when local Floci resources are not provisioned.
- Do not auto-run `terraform-apply-local`; ask for approval first.

## Next gate

Before commit/push/merge, perform a review of the Phase 13 branch diff and decide whether to:

1. polish this branch and open/update a PR; or
2. create a smaller Phase 13.2 branch focused only on trace-first workbench hardening.

Human approval is required before any commit, push, merge, rebase, branch deletion, or Terraform apply.
