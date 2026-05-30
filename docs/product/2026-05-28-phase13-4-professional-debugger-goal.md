# Phase 13.4 — Floci Studio Professional Debugger Goal

Status: implemented UI direction slice
Date: 2026-05-28

## Goal

Make Floci Studio feel like a tool a senior engineer would proudly show in an interview or portfolio walkthrough:

> “Here is a local cloud-shaped workflow. I can break it deterministically, inspect every causal step, explain the failure, and export sanitized evidence without touching real AWS.”

## What changed

The active browser surface now leads with the workflow debugger instead of a generic dashboard.

The previous dashboard-shaped hierarchy was demoted:

- API KPIs
- resource cards
- object/event inventory
- static workflow explanation
- giant generic evidence dump

The new hierarchy is:

1. failed trace queue;
2. create broken trace;
3. trace detail;
4. failure reason;
5. causal step timeline;
6. reproduction commands;
7. sanitized report;
8. supporting object evidence.

## Acceptance criteria

- User can create a deterministic broken trace from the first screen.
- UI calls `POST /ops/demo/broken-trace`.
- UI lists traces through `GET /ops/traces?status=failed`.
- UI inspects selected traces through `GET /ops/traces/{trace_id}`.
- UI exports reports through `GET /ops/report?trace_id={trace_id}`.
- Failure reason and failure code are first-class UI elements.
- Safety flags are visible: `sanitized`, `local_only`, `uses_real_cloud`, `allows_shell_execution`.
- Browser displays copyable commands but never executes shell commands.
- Copy and endpoint guards remain local-only.

## Self-critique

This still is not the final product. The next bar is to make the debugger interactive beyond the first failed trace:

- replay a corrected payload;
- compare failed vs fixed trace;
- add a timeline diff;
- persist a report artifact under evidence;
- reduce static HTML complexity into reusable components if the UI grows.

But this slice fixes the largest product problem: Floci Studio now opens on the sharp differentiator rather than generic dashboard polish.
