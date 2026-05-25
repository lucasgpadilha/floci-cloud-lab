#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.backend.functions.orchestration import run_orchestration_demo


def main() -> None:
    demo = run_orchestration_demo()
    print("orchestration demo: local Step Functions-style workflow simulation")
    print(json.dumps({"summary": demo["summary"]}, sort_keys=True))
    print(json.dumps({"success_execution": demo["success_execution"]}, sort_keys=True))
    print(json.dumps({"failure_execution": demo["failure_execution"]}, sort_keys=True))
    print(json.dumps({"aws_mapping": demo["step_functions_mapping"]}, sort_keys=True))


if __name__ == "__main__":
    main()
