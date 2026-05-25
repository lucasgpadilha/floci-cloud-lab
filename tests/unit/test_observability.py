import json

from app.backend.functions.api import create_handler
from app.backend.functions.observability import ObservabilitySink, metrics_for_request, route_template, safe_value, structured_log
from tests.unit.test_api_handler import InMemoryRepository, invoke, parse_body


def test_structured_log_contains_required_correlation_fields():
    record = structured_log(
        level="info",
        message="api request completed",
        request_id="req-123",
        method="GET",
        path="/objects/obj_123",
        status_code=200,
        latency_ms=12.3456,
        owner_id="lucas",
        object_id="obj_123",
    )

    assert record["type"] == "log"
    assert record["service"] == "floci-cloud-lab-api"
    assert record["runtime"] == "local-floci"
    assert record["request_id"] == "req-123"
    assert record["trace_id"] == "req-123"
    assert record["route"] == "GET /objects/{object_id}"
    assert record["status_class"] == "2xx"
    assert record["latency_ms"] == 12.346
    assert record["owner_id"] == "lucas"
    assert record["object_id"] == "obj_123"


def test_metrics_for_request_includes_count_latency_and_errors():
    metrics = metrics_for_request(method="POST", path="/objects", status_code=415, latency_ms=3.2, error_code="unsupported_media_type")
    names = {item["metric_name"] for item in metrics}

    assert {"ApiRequestCount", "ApiLatencyMs", "ApiErrorCount"}.issubset(names)
    error_metric = next(item for item in metrics if item["metric_name"] == "ApiErrorCount")
    assert error_metric["dimensions"]["error_code"] == "unsupported_media_type"
    assert error_metric["dimensions"]["status_class"] == "4xx"


def test_route_template_normalizes_object_id_paths():
    assert route_template("GET", "/objects/obj_abc") == "GET /objects/{object_id}"
    assert route_template("GET", "/events") == "GET /events"


def test_safe_value_redacts_secret_like_fields():
    sanitized = safe_value({"AWS_SECRET_ACCESS_KEY": "test", "nested": {"token": "abc", "ok": "yes"}})

    assert sanitized["AWS_SECRET_ACCESS_KEY"] == "***"
    assert sanitized["nested"]["token"] == "***"
    assert sanitized["nested"]["ok"] == "yes"


def test_api_handler_emits_structured_log_and_metrics():
    sink = ObservabilitySink()
    handler = create_handler(repository=InMemoryRepository(), observability_sink=sink)

    response = invoke(handler, "POST", "/objects", {"name": "obs.txt", "content": "observe me"}, headers={"x-floci-user": "lucas", "content-type": "application/json"})

    assert response["statusCode"] == 201
    assert parse_body(response)["data"]["object_id"] == "obj_test123"
    log_record = next(record for record in sink.records if record["type"] == "log")
    metric_names = {record["metric_name"] for record in sink.records if record["type"] == "metric"}
    assert log_record["request_id"] == "unit-request"
    assert log_record["route"] == "POST /objects"
    assert log_record["status_code"] == 201
    assert log_record["object_id"] == "obj_test123"
    assert {"ApiRequestCount", "ApiLatencyMs", "ObjectCreateCount"}.issubset(metric_names)


def test_api_error_emits_warn_log_and_error_metric_without_secret_leakage():
    sink = ObservabilitySink()
    handler = create_handler(repository=InMemoryRepository(), observability_sink=sink)

    response = invoke(handler, "POST", "/objects", '{"name":"x","content":"y"}', headers={"content-type": "text/plain", "authorization": "Bearer secret"})

    assert response["statusCode"] == 415
    log_record = next(record for record in sink.records if record["type"] == "log")
    error_metric = next(record for record in sink.records if record.get("metric_name") == "ApiErrorCount")
    serialized = json.dumps(sink.records)
    assert log_record["level"] == "WARN"
    assert log_record["error_code"] == "unsupported_media_type"
    assert error_metric["dimensions"]["error_code"] == "unsupported_media_type"
    assert "Bearer secret" not in serialized
