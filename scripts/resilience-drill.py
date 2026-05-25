#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.backend.functions.resilience import run_resilience_drill


def main() -> None:
    drill = run_resilience_drill()
    print("resilience drill: local-only backup/restore/failure-injection")
    print(json.dumps({"summary": drill["summary"]}, sort_keys=True))
    print(json.dumps({"manifest_checksum": drill["manifest"]["manifest_checksum"]}, sort_keys=True))
    print(json.dumps({"restore_step_names": [step["name"] for step in drill["restore_plan"]["steps"]]}, sort_keys=True))
    print(json.dumps({"failure_scenarios": [item["scenario"] for item in drill["failure_scenarios"]]}, sort_keys=True))


if __name__ == "__main__":
    main()
