SHELL := /usr/bin/env bash
PATH := $(HOME)/.local/bin:$(PATH)

FLOCI_ENDPOINT ?= http://localhost:4566
AWS_DEFAULT_REGION ?= us-east-1
AWS_ACCESS_KEY_ID ?= test
AWS_SECRET_ACCESS_KEY ?= test
PYTHON ?= python3
VENV ?= .venv

.PHONY: check docs-check no-forbidden-ci install-dev floci-up floci-down floci-health floci-env floci-smoke compose-validate shell-check terraform-fmt terraform-init-local terraform-validate terraform-plan-local terraform-drift-check terraform-apply-local python-test app-demo app-api-local app-events-process observability-demo resilience-drill orchestration-demo devops-audit pipeline

check: docs-check no-forbidden-ci terraform-fmt terraform-validate python-test

docs-check:
	@test -f README.md
	@test -f AGENTS.md
	@test -f compose.yaml
	@test -f docs/architecture.md
	@test -f docs/floci-local-workflow.md
	@test -f docs/iac-local-validation.md
	@test -f docs/ci-cd-without-actions.md
	@test -f docs/security.md
	@test -f docs/cost-learning.md
	@test -f docs/observability.md
	@test -f docs/runbook.md
	@test -f docs/devops-testing.md
	@test -f docs/iam-and-security.md
	@test -f docs/api-gateway-lambda.md
	@test -f docs/dynamodb-data-model.md
	@test -f docs/s3-object-storage.md
	@test -f docs/event-driven-architecture.md
	@test -f docs/observability-deep-dive.md
	@test -f docs/resilience-operations.md
	@test -f docs/orchestration-workflows.md
	@test -f docs/openapi/floci-cloud-lab-http-api.yaml
	@echo "docs-check: ok"

no-forbidden-ci:
	@if [ -d .github/workflows ]; then echo "ERROR: GitHub Actions workflows are forbidden for this project"; exit 1; fi
	@if find . -path './.git' -prune -o \( -name '.gitlab-ci.yml' -o -name 'gitlab-ci.yml' \) -print | grep -q .; then echo "ERROR: GitLab runner config is forbidden for this project"; exit 1; fi
	@echo "no-forbidden-ci: ok"

install-dev:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -r requirements-dev.txt

floci-up:
	./scripts/floci-up.sh

floci-down:
	./scripts/floci-down.sh

floci-health:
	./scripts/floci-health.sh

floci-env:
	@./scripts/floci-env.sh

floci-smoke:
	@./scripts/smoke-test.sh

compose-validate:
	docker compose config --quiet

shell-check:
	@find scripts -type f -name '*.sh' -print0 | xargs -0 -n1 bash -n
	@echo "shell-check: ok"

terraform-fmt:
	@if command -v terraform >/dev/null 2>&1 && find infra -name '*.tf' -print -quit | grep -q .; then 		terraform -chdir=infra/envs/local fmt -recursive ../..; 	else 		echo "terraform-fmt: skipped (terraform missing or no .tf files yet)"; 	fi

terraform-init-local:
	terraform -chdir=infra/envs/local init -backend=false

terraform-validate: terraform-init-local
	terraform -chdir=infra/envs/local validate

terraform-plan-local:
	terraform -chdir=infra/envs/local plan

terraform-drift-check:
	terraform -chdir=infra/envs/local plan -detailed-exitcode -no-color

terraform-apply-local:
	@if [ "$(FLOCI_ENDPOINT)" != "http://localhost:4566" ] && [ "$(FLOCI_ENDPOINT)" != "http://127.0.0.1:4566" ]; then \
		echo "ERROR: terraform-apply-local only supports local Floci endpoints"; \
		exit 1; \
	fi
	terraform -chdir=infra/envs/local apply -auto-approve

python-test:
	@if find tests -name 'test_*.py' -print -quit | grep -q .; then 		if [ -x $(VENV)/bin/python ]; then $(VENV)/bin/python -m pytest tests -q; else $(PYTHON) -m pytest tests -q; fi; 	else 		echo "python-test: skipped (no tests yet)"; 	fi

app-demo:
	./scripts/app-demo.sh

app-api-local:
	@if [ -x $(VENV)/bin/python ]; then $(VENV)/bin/python -m app.backend.local_server; else $(PYTHON) -m app.backend.local_server; fi

app-events-process:
	@if [ -x $(VENV)/bin/python ]; then $(VENV)/bin/python scripts/process-events.py; else $(PYTHON) scripts/process-events.py; fi

observability-demo:
	@if [ -x $(VENV)/bin/python ]; then $(VENV)/bin/python scripts/observability-demo.py; else $(PYTHON) scripts/observability-demo.py; fi

resilience-drill:
	@if [ -x $(VENV)/bin/python ]; then $(VENV)/bin/python scripts/resilience-drill.py; else $(PYTHON) scripts/resilience-drill.py; fi

orchestration-demo:
	@if [ -x $(VENV)/bin/python ]; then $(VENV)/bin/python scripts/orchestration-demo.py; else $(PYTHON) scripts/orchestration-demo.py; fi

devops-audit:
	./scripts/devops-audit.sh

pipeline: check compose-validate shell-check floci-health floci-smoke terraform-plan-local devops-audit
