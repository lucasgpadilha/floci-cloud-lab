# Floci Studio Competitive Wedge

Status: accepted product direction for Phase 13.2+
Date: 2026-05-28

## Decision

Floci Studio is **not** an AWS Console clone and is not a generic dashboard.

Floci Studio is a local-first workflow debugger for AWS-style emulator development.

Short positioning:

> Chrome DevTools for LocalStack-style / Floci-style AWS development.

Long positioning:

> Floci Studio connects to a local cloud emulator and shows resources, payloads, events, logs, and replayable traces in one place, so developers can find where a local serverless/event-driven flow broke without spelunking through CLI commands.

## Competitive rule

If a feature does not help a developer answer one of these questions, it does not belong in the MVP:

1. What exists locally?
2. What happened?
3. Where did it break?
4. Which payload caused it?
5. Can I replay it?
6. Can I reset it?
7. What is the equivalent CLI command?

## Main competitors

### LocalStack UI

LocalStack emulates and exposes a local AWS-like cloud.

Floci Studio must not compete as a broader LocalStack console.

Floci can win only by being a sharper debugging tool:

- trace-first instead of resource-admin-first;
- zero-account local-only mode;
- event/payload/replay/reset as first-class actions;
- focused inner-loop debugging, not enterprise cloud management.

Message:

> LocalStack UI shows your local cloud. Floci Studio shows why your local workflow broke.

### AWS Console

AWS Console manages production cloud. Floci Studio debugs disposable local cloud.

Do not chase:

- IAM editors;
- VPC consoles;
- billing;
- full CloudWatch dashboards;
- every service screen.

### AWS CLI / awslocal

The CLI is not an enemy. It is a trust anchor.

Every serious UI action should expose the equivalent command when practical.

Message:

> CLI is for commands. Floci Studio is for understanding.

### Service-specific tools

MinIO Console, DynamoDB Admin, queue UIs, Temporal UI, Inngest Dev Server, Supabase Studio, Grafana/Jaeger and Docker Desktop are all better in their domains.

Floci should not out-CRUD or out-observe them.

Floci wins by connecting the dots across local cloud-shaped resources:

`request -> object -> event -> worker -> database -> logs/error`

## MVP wedge

Build the best lightweight debugger for this flow:

1. HTTP/API request creates a local object.
2. Object is written to S3-compatible storage.
3. Metadata is indexed in DynamoDB-compatible storage.
4. ObjectCreated event is emitted to an outbox/queue.
5. Processor consumes or fails.
6. Developer can inspect, replay, reset, and export report.

## MVP feature list

Must have:

- `/ops/session`: adapter, capabilities, safety, service map.
- `/ops/traces`: recent flow traces.
- `/ops/traces/{trace_id}`: trace detail and steps.
- `/ops/demo/trace`: deterministic local flow demo.
- `/ops/report`: sanitized report export for a trace/session.
- UI centered on a selected flow, not KPI cards.
- Equivalent curl/awslocal commands in details.

Should have next:

- queue replay;
- reset namespace;
- failed-flow fixture;
- payload diff;
- log correlation.

Avoid:

- broad AWS service parity;
- cloud credentials;
- arbitrary shell execution;
- dashboard cards without causal meaning;
- fake metrics;
- admin CRUD as the product.

## Quality bar

A screen is allowed only if it improves one of:

- time to first insight;
- causality clarity;
- replay/reset loop;
- trust/transparency;
- local safety.

If it only makes the app look bigger, remove it.
