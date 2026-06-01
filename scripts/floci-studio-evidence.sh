#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR" || exit 1

EVIDENCE_FILE="${EVIDENCE_FILE:-evidence/floci-studio-trace-debugger.md}"
FLOCI_ENDPOINT="${FLOCI_ENDPOINT:-http://localhost:4566}"
AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-$FLOCI_ENDPOINT}"
API_URL="${API_URL:-http://127.0.0.1:8080}"
OWNER_ID="${OWNER_ID:-portfolio-evidence}"
TMP_FILE=""
FAILED=0
BROKEN_TRACE_ID=""

case "$FLOCI_ENDPOINT" in
  http://localhost:4566|http://127.0.0.1:4566) ;;
  *)
    printf 'ERROR: refusing non-local FLOCI_ENDPOINT=%s\n' "$FLOCI_ENDPOINT" >&2
    exit 1
    ;;
esac

case "$AWS_ENDPOINT_URL" in
  http://localhost:4566|http://127.0.0.1:4566) ;;
  *)
    printf 'ERROR: refusing non-local AWS_ENDPOINT_URL=%s\n' "$AWS_ENDPOINT_URL" >&2
    exit 1
    ;;
esac

case "$API_URL" in
  http://localhost:8080|http://127.0.0.1:8080) ;;
  *)
    printf 'ERROR: refusing non-local API_URL=%s\n' "$API_URL" >&2
    exit 1
    ;;
esac

if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
else
  PY=python3
fi

mkdir -p "$(dirname "$EVIDENCE_FILE")" || exit 1
TMP_FILE="$(mktemp "${TMPDIR:-/tmp}/floci-studio-evidence.XXXXXX")" || exit 1
trap 'if [ -n "${TMP_FILE:-}" ] && [ -f "$TMP_FILE" ]; then rm -f "$TMP_FILE"; fi' EXIT

now_utc() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

sanitize_stream() {
  sed -E \
    -e 's/(AWS_ACCESS_KEY_ID=)[^[:space:]]+/\1[REDACTED]/g' \
    -e 's/(AWS_SECRET_ACCESS_KEY=)[^[:space:]]+/\1[REDACTED]/g' \
    -e 's/(AWS_SESSION_TOKEN=)[^[:space:]]+/\1[REDACTED]/g' \
    -e 's/((secret|token|password|credential)[_A-Za-z0-9-]*[=:][[:space:]]*)[^[:space:],}]+/\1[REDACTED]/Ig' \
    -e 's/AKIA[0-9A-Z]{16}/[REDACTED_AWS_ACCESS_KEY]/g'
}

json_pretty() {
  "$PY" -m json.tool 2>/dev/null || cat
}

append_endpoint() {
  local title="$1"
  local method="$2"
  local path="$3"
  local status_file body_file status rc
  status_file="$(mktemp "${TMPDIR:-/tmp}/floci-status.XXXXXX")" || exit 1
  body_file="$(mktemp "${TMPDIR:-/tmp}/floci-body.XXXXXX")" || exit 1

  {
    printf '\n## %s\n\n' "$title"
    printf -- '- Started: `%s`\n' "$(now_utc)"
    printf -- '- Request: `%s %s%s`\n\n' "$method" "$API_URL" "$path"
    printf '```json\n'
  } >> "$TMP_FILE"

  set +e
  curl -sS -X "$method" \
    -H "x-floci-user: $OWNER_ID" \
    -H 'content-type: application/json' \
    -o "$body_file" \
    -w '%{http_code}' \
    "$API_URL$path" > "$status_file" 2>> "$body_file"
  rc=$?
  set -e

  status="$(cat "$status_file")"
  if [ "$rc" -ne 0 ]; then
    FAILED=1
    printf '{"request_failed":true,"curl_exit_code":%s,"hint":"Start the local API with make app-api-local before capturing runtime evidence."}\n' "$rc" >> "$TMP_FILE"
  else
    cat "$body_file" | sanitize_stream | json_pretty >> "$TMP_FILE"
  fi

  {
    printf '\n```\n\n'
    printf -- '- HTTP status: `%s`\n' "${status:-unavailable}"
    printf -- '- Finished: `%s`\n' "$(now_utc)"
    printf '\n'
  } >> "$TMP_FILE"

  if [ "$rc" -eq 0 ] && [ "$status" != "200" ] && [ "$status" != "201" ]; then
    FAILED=1
  fi

  if [ "$path" = "/ops/demo/broken-trace" ] && [ "$rc" -eq 0 ]; then
    BROKEN_TRACE_ID="$($PY - "$body_file" <<'PY' 2>/dev/null
import json, sys
with open(sys.argv[1], encoding='utf-8') as fh:
    data=json.load(fh)
print(data.get('trace', {}).get('id', ''))
PY
)"
  fi

  rm -f "$status_file" "$body_file"
}

{
  printf '# Floci Studio Trace Debugger Evidence\n\n'
  printf -- '- Captured at: `%s`\n' "$(now_utc)"
  printf -- '- Worktree: `%s`\n' "$ROOT_DIR"
  printf -- '- API URL: `%s`\n' "$API_URL"
  printf -- '- Floci endpoint policy: local-only (`%s`)\n' "$FLOCI_ENDPOINT"
  printf -- '- AWS SDK endpoint policy: local-only (`%s`)\n' "$AWS_ENDPOINT_URL"
  printf -- '- Owner namespace: `%s`\n' "$OWNER_ID"
  printf -- '- Terraform safety: this capture never runs `terraform apply` or provisions resources automatically.\n'
  printf -- '- Secret safety: output is sanitized before being written.\n\n'
  printf '## What this proves\n\n'
  printf 'This evidence captures the Floci Studio differentiator: a local workflow debugger for AWS-shaped flows. The goal is not to show a generic resource dashboard; it is to show request → object storage → metadata → outbox event → processor result, including a deterministic broken flow and sanitized report export.\n'
} > "$TMP_FILE" || exit 1

append_endpoint "Health check" GET /health
append_endpoint "Local session / capability discovery" GET /ops/session
append_endpoint "Create deterministic broken trace" POST /ops/demo/broken-trace

if [ -n "$BROKEN_TRACE_ID" ]; then
  append_endpoint "Read broken trace detail" GET "/ops/traces/$BROKEN_TRACE_ID"
  append_endpoint "Export sanitized trace report" GET "/ops/report?trace_id=$BROKEN_TRACE_ID"
else
  {
    printf '\n## Trace detail/report skipped\n\n'
    printf 'The broken trace step did not return a trace id. If the API returned `local_dependency_unavailable`, provision the local Floci bucket/table through the approved local setup path, then rerun this script.\n'
  } >> "$TMP_FILE"
fi

{
  printf '\n## Reviewer notes\n\n'
  printf -- '- If all endpoint statuses are 200/201, the first-click debugger path is runtime-verified.\n'
  printf -- '- If demo endpoints return 503 `local_dependency_unavailable`, the API is still behaving correctly for missing local emulator resources; do not auto-run Terraform apply without approval.\n'
  printf -- '- This file is safe to include in a portfolio review because it contains only local emulator evidence and sanitized output.\n'
} >> "$TMP_FILE"

mv "$TMP_FILE" "$EVIDENCE_FILE" || exit 1
TMP_FILE=""
chmod 0644 "$EVIDENCE_FILE" 2>/dev/null || true

if [ "$FAILED" -ne 0 ]; then
  printf 'Evidence captured with runtime blockers: %s\n' "$EVIDENCE_FILE" >&2
  exit 1
fi

printf 'Evidence captured: %s\n' "$EVIDENCE_FILE"
