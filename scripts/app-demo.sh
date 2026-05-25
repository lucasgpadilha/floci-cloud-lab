#!/usr/bin/env bash
set -euo pipefail

export AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
export FLOCI_OBJECT_BUCKET="${FLOCI_OBJECT_BUCKET:-floci-cloud-lab-local-objects}"
export FLOCI_METADATA_TABLE="${FLOCI_METADATA_TABLE:-floci-cloud-lab-local-metadata}"

if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
else
  PY=python3
fi

$PY - <<'PY'
import json
from app.backend.functions.api import lambda_handler


def invoke(method, path, body=None, user="cli-demo", query=None):
    event = {
        "requestContext": {"http": {"method": method, "path": path}},
        "headers": {"x-floci-user": user, "content-type": "application/json"},
        "queryStringParameters": query or {},
        "body": json.dumps(body) if body is not None else None,
    }
    response = lambda_handler(event, None)
    print(f"\n{method} {path} -> {response['statusCode']}")
    print(json.dumps(json.loads(response["body"]), indent=2, sort_keys=True))
    return response

invoke("GET", "/health")
created = invoke(
    "POST",
    "/objects",
    {
        "name": "cli-demo.txt",
        "content": "Created by scripts/app-demo.sh through the local API handler",
        "content_type": "text/plain",
        "metadata": {"source": "app-demo"},
    },
)
object_id = json.loads(created["body"])["data"]["object_id"]
invoke("GET", "/objects")
invoke("GET", f"/objects/{object_id}")
invoke("GET", "/events", query={"status": "pending"})
invoke("POST", "/events/process")
invoke("GET", "/events")
PY
