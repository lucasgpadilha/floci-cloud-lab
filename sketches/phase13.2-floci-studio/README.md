## Variant: Floci Studio — Flow Inspector

### Design stance

Move away from dark generic dashboard patterns into a product-specific local studio: closer to a database studio + trace recorder + local debugger.

### Why it is different from the previous sketch

- No cloud-console cosplay as the main identity.
- No big dark SaaS dashboard grid.
- No generic KPI cards; status appears only where it helps the flow.
- The main visual object is a flow map tied to a selected trace.
- The right side reads like a technical artifact/report, not a decorative card column.
- Warmer paper-like surfaces make it feel less like AI dark-dashboard sludge.

### Product bet

The core unit is a recorded local flow:

`request -> API -> object store -> metadata -> outbox -> processor`

### Still missing before it becomes production-worthy

- Real `/ops/session` and `/ops/traces` endpoints.
- Real selected trace data instead of mocked rows.
- True logs panel and report export.
- Interaction polish: keyboard command palette, hover states, selected-node filtering.

### How to open

```bash
cd /home/lucas/agentic/runs/floci-cloud-lab-gemini-phase13
python3 -m http.server 5176 -d sketches/phase13.2-floci-studio --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:5176
```
