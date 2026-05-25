import json

from app.backend.local_server import build_lambda_event


def test_build_lambda_event_includes_query_string_parameters():
    event = build_lambda_event(
        method="GET",
        path="/objects?limit=2&cursor=abc&category=notes",
        headers={"x-request-id": "local-test"},
        body=b"",
    )

    assert event["rawPath"] == "/objects"
    assert event["rawQueryString"] == "limit=2&cursor=abc&category=notes"
    assert event["queryStringParameters"] == {"limit": "2", "cursor": "abc", "category": "notes"}


def test_list_objects_accepts_pagination_query_parameters():
    calls = []

    class Repository:
        def list_objects(self, *, owner_id, limit=25, cursor=None, category=None):
            calls.append({"owner_id": owner_id, "limit": limit, "cursor": cursor, "category": category})
            return {"count": 0, "objects": [], "next_cursor": None}

    from app.backend.functions.api import create_handler

    handler = create_handler(repository=Repository())
    response = handler(
        {
            "version": "2.0",
            "rawPath": "/objects",
            "queryStringParameters": {"limit": "2", "cursor": "abc", "category": "notes"},
            "requestContext": {"requestId": "req", "http": {"method": "GET", "path": "/objects"}},
            "headers": {"x-floci-user": "lucas"},
            "body": None,
            "isBase64Encoded": False,
        },
        None,
    )

    assert response["statusCode"] == 200
    assert calls == [{"owner_id": "lucas", "limit": 2, "cursor": "abc", "category": "notes"}]
    assert json.loads(response["body"])["data"] == {"count": 0, "objects": [], "next_cursor": None}
