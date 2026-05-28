#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR" || exit 1

EVIDENCE_FILE="${EVIDENCE_FILE:-evidence/pipeline-latest.md}"
TMP_FILE=""
FLOCI_ENDPOINT="${FLOCI_ENDPOINT:-http://localhost:4566}"
AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-$FLOCI_ENDPOINT}"
AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
export FLOCI_ENDPOINT AWS_ENDPOINT_URL AWS_DEFAULT_REGION AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY

case "$FLOCI_ENDPOINT" in
  http://localhost:4566|http://127.0.0.1:4566) ;;
  *)
    printf 'ERROR: refusing to capture evidence for non-local FLOCI_ENDPOINT=%s\n' "$FLOCI_ENDPOINT" >&2
    exit 1
    ;;
esac

case "$AWS_ENDPOINT_URL" in
  http://localhost:4566|http://127.0.0.1:4566) ;;
  *)
    printf 'ERROR: refusing to capture evidence for non-local AWS_ENDPOINT_URL=%s\n' "$AWS_ENDPOINT_URL" >&2
    exit 1
    ;;
esac

mkdir -p "$(dirname "$EVIDENCE_FILE")" || exit 1
umask 077
TMP_FILE="$(mktemp "${TMPDIR:-/tmp}/floci-pipeline-evidence.XXXXXX")" || exit 1
trap 'if [ -n "${TMP_FILE:-}" ] && [ -f "$TMP_FILE" ]; then rm -f "$TMP_FILE"; fi' EXIT

now_utc() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

sanitize_stream() {
  sed -E \
    -e 's/(AWS_ACCESS_KEY_ID=)[^[:space:]]+/\1[REDACTED]/g' \
    -e 's/(AWS_SECRET_ACCESS_KEY=)[^[:space:]]+/\1[REDACTED]/g' \
    -e 's/(AWS_SESSION_TOKEN=)[^[:space:]]+/\1[REDACTED]/g' \
    -e 's/((secret|token|password|credential)[_A-Za-z0-9-]*[=:][[:space:]]*)[^[:space:]]+/\1[REDACTED]/Ig' \
    -e 's/AKIA[0-9A-Z]{16}/[REDACTED_AWS_ACCESS_KEY]/g' \
    -e 's/(aws_secret_access_key[[:space:]]*=[[:space:]]*)"?[^"]+"?/\1[REDACTED]/Ig'
}

run_and_capture() {
  local title="$1"
  shift
  local rc

  {
    printf '\n## %s\n\n' "$title"
    printf -- '- Started: `%s`\n' "$(now_utc)"
    printf -- '- Command: `%s`\n\n' "$*"
    printf '```text\n'
  } >> "$TMP_FILE"

  set +e
  "$@" 2>&1 | sanitize_stream >> "$TMP_FILE"
  rc=${PIPESTATUS[0]}
  set -e

  {
    printf '```\n\n'
    printf -- '- Finished: `%s`\n' "$(now_utc)"
    printf -- '- Exit code: `%s`\n' "$rc"
    printf '\n'
  } >> "$TMP_FILE"

  if [ "$rc" -ne 0 ]; then
    FAILED=1
  fi
}

FAILED=0
{
  printf '# Local Pipeline Evidence\n\n'
  printf -- '- Captured at: `%s`\n' "$(now_utc)"
  printf -- '- Worktree: `%s`\n' "$ROOT_DIR"
  printf -- '- Endpoint policy: local Floci only (`%s`)\n' "$FLOCI_ENDPOINT"
  printf -- '- Credential policy: fake local credentials only; secret-looking values are redacted.\n'
  printf -- '- Exclusions: this script does not collect `.env`, `.terraform/`, `*.tfstate`, `.venv/`, cache directories, or full environment dumps.\n'
  printf -- '- Terraform safety: validation and plan are allowed; `terraform apply` is not run by this capture.\n\n'
} > "$TMP_FILE" || exit 1

run_and_capture "Git status before evidence capture" git status --short
run_and_capture "Canonical local CI pipeline" make pipeline
run_and_capture "Compatibility check target" make check
run_and_capture "Whitespace diff check" git diff --check
run_and_capture "Forbidden hosted CI guard" make no-forbidden-ci

mv "$TMP_FILE" "$EVIDENCE_FILE" || exit 1
TMP_FILE=""
chmod 0644 "$EVIDENCE_FILE" 2>/dev/null || true

if [ "$FAILED" -ne 0 ]; then
  printf 'Evidence captured with failures: %s\n' "$EVIDENCE_FILE" >&2
  exit 1
fi

printf 'Evidence captured: %s\n' "$EVIDENCE_FILE"
