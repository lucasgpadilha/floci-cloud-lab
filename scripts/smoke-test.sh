#!/usr/bin/env bash
set -euo pipefail

export AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"

if [ -x .venv/bin/python ]; then
  .venv/bin/python -m pytest tests/smoke -q
else
  python3 -m pytest tests/smoke -q
fi
