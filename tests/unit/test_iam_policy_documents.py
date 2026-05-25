import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "infra" / "modules" / "iam" / "policy-documents"
POLICY_FILES = sorted(POLICY_DIR.glob("*.json"))


def iter_values(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from iter_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_values(item)
    else:
        yield value


def statement_list(policy):
    statements = policy.get("Statement")
    assert isinstance(statements, list), "Policy Statement must be a list"
    return statements


def as_list(value):
    return value if isinstance(value, list) else [value]


def test_iam_policy_documents_exist_and_are_valid_json():
    assert POLICY_FILES, "Expected IAM policy JSON documents"

    for path in POLICY_FILES:
        policy = json.loads(path.read_text(encoding="utf-8"))
        assert policy["Version"] == "2012-10-17"
        assert statement_list(policy)


def test_iam_policy_documents_do_not_use_exact_action_or_resource_wildcards():
    for path in POLICY_FILES:
        policy = json.loads(path.read_text(encoding="utf-8"))
        for statement in statement_list(policy):
            sid = statement.get("Sid", f"statement in {path.name}")
            for key in ("Action", "NotAction"):
                if key in statement:
                    assert "*" not in as_list(statement[key]), f"{sid} uses exact wildcard {key}"
            for key in ("Resource", "NotResource"):
                if key in statement:
                    assert "*" not in as_list(statement[key]), f"{sid} uses exact wildcard {key}"


def test_app_permissions_policy_scopes_expected_services_only():
    policy = json.loads((POLICY_DIR / "app-permissions.json").read_text(encoding="utf-8"))
    actions = {
        action
        for statement in statement_list(policy)
        for action in as_list(statement.get("Action", []))
    }

    allowed_prefixes = ("s3:", "dynamodb:", "logs:")
    assert actions
    assert all(action.startswith(allowed_prefixes) for action in actions)
    assert "iam:PassRole" not in actions
    assert "sts:AssumeRole" not in actions


def test_policy_documents_reference_local_lab_resources():
    combined_values = "\n".join(
        str(value)
        for path in POLICY_FILES
        for value in iter_values(json.loads(path.read_text(encoding="utf-8")))
    )

    assert "floci-cloud-lab-local-objects" in combined_values
    assert "floci-cloud-lab-local-metadata" in combined_values
    assert "/floci-cloud-lab/local/app" in combined_values
