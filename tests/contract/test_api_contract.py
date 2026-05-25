import json

from app.backend.functions.api import create_handler
from tests.unit.test_api_handler import InMemoryRepository


def http_api_v2_event(method, path, *, body=None, headers=None, request_id="contract-request"):
    return {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "rawQueryString": "",
        "headers": headers or {},
        "requestContext": {
            "accountId": "000000000000",
            "apiId": "local-floci-http-api",
            "domainName": "localhost",
            "domainPrefix": "localhost",
            "requestId": request_id,
            "routeKey": f"{method} {path}",
            "stage": "$default",
            "time": "25/May/2026:10:30:00 +0000",
            "timeEpoch": 1779705000000,
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "contract-test",
            },
        },
        "body": json.dumps(body) if isinstance(body, dict) else body,
        "isBase64Encoded": False,
    }


def parse(response):
    return json.loads(response["body"]) if response.get("body") else {}


def test_http_api_v2_create_contract_has_gateway_shape_and_request_id():
    handler = create_handler(repository=InMemoryRepository())
    event = http_api_v2_event(
        "POST",
        "/objects",
        headers={"content-type": "application/json", "x-floci-user": "contract-user"},
        body={"name": "contract.txt", "content": "hello contract"},
    )

    response = handler(event, None)

    assert response["statusCode"] == 201
    assert response["isBase64Encoded"] is False
    assert response["headers"]["content-type"] == "application/json"
    assert response["headers"]["x-request-id"] == "contract-request"
    body = parse(response)
    assert body["request_id"] == "contract-request"
    assert body["data"]["owner_id"] == "contract-user"


def test_http_api_v2_validation_error_contract():
    handler = create_handler(repository=InMemoryRepository())
    event = http_api_v2_event("POST", "/objects", headers={"content-type": "application/json"}, body={"name": ""})

    response = handler(event, None)

    assert response["statusCode"] == 400
    body = parse(response)
    assert body["request_id"] == "contract-request"
    assert body["error"]["code"] == "validation_error"
    assert "content" in body["error"]["message"] or "name" in body["error"]["message"]


def test_http_api_v2_cors_preflight_contract():
    handler = create_handler(repository=InMemoryRepository())
    event = http_api_v2_event("OPTIONS", "/objects")

    response = handler(event, None)

    assert response["statusCode"] == 204
    assert response["body"] == ""
    assert response["headers"]["access-control-allow-origin"] == "*"
    assert "x-request-id" in response["headers"]["access-control-expose-headers"]


def test_http_api_v2_not_found_contract():
    handler = create_handler(repository=InMemoryRepository())
    event = http_api_v2_event("GET", "/objects/missing", headers={"x-floci-user": "contract-user"})

    response = handler(event, None)

    assert response["statusCode"] == 404
    assert parse(response)["error"]["code"] == "not_found"
