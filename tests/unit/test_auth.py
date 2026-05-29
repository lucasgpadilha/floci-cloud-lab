from app.backend.functions.auth import owner_from_event, request_id_from_event


def test_owner_from_event_accepts_portfolio_safe_identifiers():
    event = {"headers": {"x-floci-user": "lucas.dev-01"}}

    assert owner_from_event(event) == "lucas.dev-01"


def test_owner_from_event_rejects_shell_metacharacters_to_safe_default():
    event = {"headers": {"x-floci-user": "lucas'; rm -rf / #"}}

    assert owner_from_event(event) == "local-user"


def test_request_id_rejects_control_characters_to_prevent_header_injection():
    event = {"headers": {"x-request-id": "ok\r\nX-Evil: 1"}, "requestContext": {"requestId": "context-id"}}

    assert request_id_from_event(event) == "context-id"


def test_request_id_falls_back_when_all_candidates_are_unsafe():
    event = {"headers": {"x-request-id": "bad\nvalue"}, "requestContext": {"requestId": "also bad\r"}}

    assert request_id_from_event(event) == "local-request"
