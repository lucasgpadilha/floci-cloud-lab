#!/usr/bin/env bash
set -euo pipefail

APP_PORT="${APP_PORT:-8080}"
COMPOSE_FILES=(-f compose.container.yaml)

cleanup() {
  docker compose "${COMPOSE_FILES[@]}" down --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

if ! command -v docker >/dev/null 2>&1; then
  echo "container demo: skipped (docker command not found)"
  exit 0
fi

if ! docker info >/dev/null 2>&1; then
  echo "container demo: skipped (docker daemon unavailable)"
  exit 0
fi

echo "container demo: build local app image"
docker compose "${COMPOSE_FILES[@]}" build app

echo "container demo: start floci + app"
docker compose "${COMPOSE_FILES[@]}" up -d floci app

echo "container demo: wait for app health on http://127.0.0.1:${APP_PORT}/health"
for attempt in {1..30}; do
  if python3 - "$APP_PORT" <<'PY' >/tmp/floci-cloud-lab-container-health.json 2>/dev/null
import json
import sys
import urllib.request
port = sys.argv[1]
with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as response:
    payload = json.loads(response.read().decode("utf-8"))
    assert response.status == 200
    assert payload.get("ok") is True
    print(json.dumps(payload, sort_keys=True))
PY
  then
    break
  fi
  if [ "$attempt" -eq 30 ]; then
    echo "container demo: app did not become healthy" >&2
    docker compose "${COMPOSE_FILES[@]}" ps
    docker compose "${COMPOSE_FILES[@]}" logs --tail=80 app >&2 || true
    exit 1
  fi
  sleep 2
done

HEALTH_JSON="$(cat /tmp/floci-cloud-lab-container-health.json)"
APP_CONTAINER_ID="$(docker compose "${COMPOSE_FILES[@]}" ps -q app)"
APP_HEALTH="none"
for attempt in {1..10}; do
  APP_HEALTH="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$APP_CONTAINER_ID")"
  if [ "$APP_HEALTH" = "healthy" ]; then
    break
  fi
  sleep 1
done

echo "container demo: health ${HEALTH_JSON}"
echo "container demo: docker health ${APP_HEALTH}"
echo "container demo: services"
docker compose "${COMPOSE_FILES[@]}" ps --format json | python3 -c 'import json,sys; rows=[json.loads(line) for line in sys.stdin if line.strip()]; print(json.dumps([{"name": r.get("Name"), "service": r.get("Service"), "state": r.get("State"), "health": r.get("Health", "")} for r in rows], sort_keys=True))'
