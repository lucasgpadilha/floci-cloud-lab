#!/usr/bin/env bash
set -euo pipefail

endpoint="${FLOCI_ENDPOINT:-http://localhost:4566}"
health_url="${endpoint%/}/_localstack/health"

for _ in {1..30}; do
  if curl -fsS "$health_url" >/dev/null 2>&1; then
    echo "floci-health: ok ($health_url)"
    exit 0
  fi
  sleep 1
done

echo "floci-health: failed to reach $health_url" >&2
exit 1
