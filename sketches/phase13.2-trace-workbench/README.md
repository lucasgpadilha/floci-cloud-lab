## Variant: Trace-first Local Cloud Workbench

### Design stance

A serious local developer workbench centered on causal traces, not KPI cards or fake cloud-console surfaces.

### Key choices

- Layout: three-pane app shell — navigation, recent traces, selected trace inspector — with topology strip fixed at the bottom.
- Typography: restrained system sans with monospace for IDs, paths, endpoints, payloads and commands.
- Color: neutral dark palette with one blue/violet accent and semantic status only.
- Interaction concept: select a trace, inspect timeline, copy repro/export report, run bounded safe local actions.

### Why this avoids AI slop

- The hero object is a real workflow trace.
- Every visual element maps to an operational question: what happened, where data went, what event was emitted, what can I safely do next.
- AWS concepts are secondary compatibility metadata, not product identity.
- No fake charts, no executive KPIs, no ornamental cards.

### Trade-offs

- Strong at debugging and product credibility.
- Weaker as a general “resource catalog” until capability discovery and resource drill-down are implemented.
- Requires backend trace/session endpoints to become truly real.

### Best for

Floci Cloud Lab Phase 13.2 and future OSS `Local Cloud Workbench` direction.

### How to open

From repo/worktree root:

```bash
python3 -m http.server 5175 -d sketches/phase13.2-trace-workbench
```

Then open:

```text
http://127.0.0.1:5175
```
