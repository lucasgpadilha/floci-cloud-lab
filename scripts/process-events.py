#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.backend.functions.api import lambda_handler


def main() -> int:
    event = {
        "requestContext": {"http": {"method": "POST", "path": "/events/process"}},
        "headers": {"x-floci-user": "cli-demo"},
        "queryStringParameters": {},
        "body": None,
        "isBase64Encoded": False,
    }
    response = lambda_handler(event, None)
    print(json.dumps(json.loads(response["body"]), indent=2, sort_keys=True))
    return 0 if response["statusCode"] == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
