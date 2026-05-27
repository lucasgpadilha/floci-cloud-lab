from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text()


def test_dockerfile_runs_local_api_adapter_and_exposes_healthcheck():
    dockerfile = read("Dockerfile")

    assert "FROM python:" in dockerfile
    assert "app.backend.local_server" in dockerfile
    assert "--host" in dockerfile
    assert "0.0.0.0" in dockerfile
    assert "EXPOSE 8080" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "http://127.0.0.1:8080/health" in dockerfile


def test_dockerfile_uses_fake_local_defaults_not_real_aws_endpoints():
    dockerfile = read("Dockerfile")

    assert "FLOCI_ENDPOINT=http://floci:4566" in dockerfile
    assert "AWS_ACCESS_KEY_ID=test" in dockerfile
    assert "AWS_SECRET_ACCESS_KEY=test" in dockerfile
    assert "amazonaws.com" not in dockerfile


def test_dockerignore_excludes_secret_and_state_material():
    dockerignore = read(".dockerignore")

    for pattern in [".env", ".terraform", "*.tfstate", ".venv", "__pycache__"]:
        assert pattern in dockerignore
    assert "!.env.example" in dockerignore


def test_compose_container_uses_local_floci_service_and_healthcheck():
    compose = read("compose.container.yaml")

    assert "app:" in compose
    assert "image: floci-cloud-lab-app:local" in compose
    assert "FLOCI_ENDPOINT: http://floci:4566" in compose
    assert "AWS_ACCESS_KEY_ID: test" in compose
    assert "AWS_SECRET_ACCESS_KEY: test" in compose
    assert "healthcheck:" in compose
    assert "depends_on:" in compose
    assert "amazonaws.com" not in compose


def test_makefile_exposes_container_targets_and_docs_check():
    makefile = read("Makefile")

    assert "app-container-build" in makefile
    assert "app-container-demo" in makefile
    assert "compose-container-validate" in makefile
    assert "docs/containers-ecs.md" in makefile


def test_container_demo_is_local_only_and_handles_missing_docker():
    script = read("scripts/container-demo.sh")

    assert "docker compose" in script
    assert "compose.container.yaml" in script
    assert "docker command not found" in script
    assert "docker daemon unavailable" in script
    assert "http://127.0.0.1:${APP_PORT}/health" in script
    assert "aws " not in script
