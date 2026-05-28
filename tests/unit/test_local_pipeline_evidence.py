from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_makefile_exposes_pipeline_and_evidence_targets():
    makefile = read("Makefile")

    assert "pipeline:" in makefile
    assert "evidence:" in makefile
    assert "./scripts/capture-evidence.sh" in makefile

    expected_order = [
        "docs-check",
        "no-forbidden-ci",
        "local-endpoint-check",
        "shell-check",
        "compose-validate",
        "compose-container-validate",
        "k8s-validate",
        "terraform-fmt",
        "terraform-validate",
        "python-test",
        "floci-health",
        "floci-smoke",
        "terraform-plan-local",
    ]
    steps_line = next(line for line in makefile.splitlines() if 'steps="' in line)
    positions = [steps_line.index(target) for target in expected_order]
    assert positions == sorted(positions)


def test_evidence_capture_is_local_only_and_sanitized():
    script = read("scripts/capture-evidence.sh")

    assert "http://localhost:4566" in script
    assert "http://127.0.0.1:4566" in script
    assert "AWS_ENDPOINT_URL" in script
    assert "refusing to capture evidence for non-local" in script
    assert "sanitize_stream" in script
    assert "AWS_SECRET_ACCESS_KEY" in script
    assert "[REDACTED]" in script
    assert "terraform apply" in script
    assert "make pipeline" in script
    assert "git diff --check" in script
    assert ".terraform/" in script
    assert "*.tfstate" in script
    assert ".env" in script


def test_release_and_agentic_docs_describe_approval_gates_and_forbidden_ci():
    release = read("docs/release-process.md")
    workflow = read("docs/agentic-delivery-workflow.md")

    for text in (release, workflow):
        assert "make pipeline" in text
        assert "make evidence" in text
        assert "evidence/pipeline-latest.md" in text
        assert ".github/workflows" in text
        assert ".gitlab-ci.yml" in text
        assert "terraform apply" in text
        assert "approval" in text.lower()

    assert "CodeBuild-style" in release
    assert "isolated worktree" in workflow
