from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_makefile_exposes_devops_audit_targets():
    makefile = read("Makefile")

    assert "devops-audit:" in makefile
    assert "terraform-drift-check:" in makefile
    assert "compose-validate:" in makefile
    assert "shell-check:" in makefile


def test_devops_audit_script_blocks_real_aws_endpoints_by_default():
    script = read("scripts/devops-audit.sh")

    assert "amazonaws.com" in script
    assert "http://localhost:4566" in script
    assert "terraform plan -detailed-exitcode" in script


def test_compose_uses_local_floci_port_and_memory_storage():
    compose = read("compose.yaml")

    assert "4566:4566" in compose
    assert "FLOCI_STORAGE_MODE: memory" in compose
    assert "floci/floci" in compose
