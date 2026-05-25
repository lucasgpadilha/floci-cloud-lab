#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

FLOCI_ENDPOINT="${FLOCI_ENDPOINT:-http://localhost:4566}"
TF_DIR="infra/envs/local"

log() { printf '\n== %s ==\n' "$*"; }
ok() { printf 'ok: %s\n' "$*"; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

case "$FLOCI_ENDPOINT" in
  http://localhost:4566|http://127.0.0.1:4566) ;;
  *) fail "FLOCI_ENDPOINT must be local-only, got: $FLOCI_ENDPOINT" ;;
esac

log "forbidden CI guard"
if [ -d .github/workflows ]; then
  fail "GitHub Actions workflows are forbidden for this project"
fi
if find . -path './.git' -prune -o \( -name '.gitlab-ci.yml' -o -name 'gitlab-ci.yml' \) -print | grep -q .; then
  fail "GitLab runner config is forbidden for this project"
fi
ok "no forbidden CI files"

log "real AWS endpoint guard"
if grep -RIn --exclude='devops-audit.sh' --exclude='*.tfstate' --exclude='*.tfstate.*' --exclude-dir='.git' --exclude-dir='.terraform' --exclude-dir='.venv' \
  'amazonaws.com\|AWS_ACCESS_KEY_ID=.*AKIA' \
  Makefile compose.yaml app infra scripts 2>/dev/null; then
  fail "operational files contain real AWS endpoint or credential-looking values"
fi
if grep -RIn --exclude-dir='.git' --exclude-dir='.terraform' --exclude-dir='.venv' \
  'http://localhost:4566' infra app scripts tests Makefile >/dev/null; then
  ok "local Floci endpoint is explicit in operational files"
else
  fail "local Floci endpoint not found in operational files"
fi
ok "no real AWS endpoint patterns found"

log "IAM wildcard policy guard"
if grep -RInE --include='*.json' --include='*.tf' --exclude-dir='.terraform' \
  '"(Action|Resource)"[[:space:]]*:[[:space:]]*"\\*"|"(Action|Resource)"[[:space:]]*:[[:space:]]*\[[^]]*"\\*"|\b(actions|resources)[[:space:]]*=[[:space:]]*\[[^]]*"\\*"' \
  infra/modules/iam 2>/dev/null; then
  fail "IAM policy documents contain exact wildcard Action or Resource"
fi
ok "IAM policy documents avoid exact wildcard Action/Resource"

log "shell syntax"
while IFS= read -r script; do
  bash -n "$script"
  ok "bash -n $script"
done < <(find scripts -type f -name '*.sh' | sort)

log "docker compose validation"
if command -v docker >/dev/null 2>&1; then
  docker compose config --quiet
  ok "docker compose config"
else
  fail "docker command missing"
fi

log "terraform fmt/validate/drift"
# Drift detection intentionally uses: terraform plan -detailed-exitcode
command -v terraform >/dev/null 2>&1 || fail "terraform command missing"
terraform -chdir="$TF_DIR" fmt -check -recursive ../..
terraform -chdir="$TF_DIR" init -backend=false >/dev/null
terraform -chdir="$TF_DIR" validate
set +e
terraform -chdir="$TF_DIR" plan -detailed-exitcode -no-color >/tmp/floci-cloud-lab-plan.txt
plan_rc=$?
set -e
case "$plan_rc" in
  0) ok "terraform plan has no drift" ;;
  1) cat /tmp/floci-cloud-lab-plan.txt >&2; fail "terraform plan failed" ;;
  2) cat /tmp/floci-cloud-lab-plan.txt >&2; fail "terraform drift detected" ;;
  *) cat /tmp/floci-cloud-lab-plan.txt >&2; fail "unexpected terraform plan exit code: $plan_rc" ;;
esac

log "python tests"
if [ -x .venv/bin/python ]; then
  .venv/bin/python -m pytest tests -q
else
  python3 -m pytest tests -q
fi

log "devops audit complete"
ok "local-only DevOps audit passed"
