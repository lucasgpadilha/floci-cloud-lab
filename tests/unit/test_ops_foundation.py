from app.backend.functions.ops.reports import build_sanitized_trace_report
from app.backend.functions.ops.session import build_ops_session
from app.backend.functions.ops.traces import TraceEvent, build_trace_detail, build_trace_list, trace_id_for_event


def pending_event():
    return {
        "event_id": "evt_foundation",
        "event_type": "ObjectCreated",
        "owner_id": "lucas",
        "object_id": "obj_foundation",
        "status": "pending",
        "attempts": 0,
        "detail": {
            "bucket": "floci-cloud-lab-local-objects",
            "key": "objects/lucas/obj_foundation/demo.md",
            "content_type": "text/markdown",
            "size_bytes": 42,
            "sha256": "abc123",
        },
    }


def test_ops_session_contract_is_adapter_agnostic_and_local_safe():
    session = build_ops_session(owner_id="lucas", request_id="req-1")

    assert session["session"]["id"] == "local-lucas"
    assert session["positioning"] == "local-cloud-workflow-debugger"
    assert session["adapter"]["name"] == "floci"
    assert session["safety"] == {
        "local_only": True,
        "uses_real_cloud": False,
        "uses_real_credentials": False,
        "allows_shell_execution": False,
        "bounded_mutations_only": True,
    }
    assert [node["id"] for node in session["service_map"]] == [
        "client",
        "api",
        "object-store",
        "metadata-store",
        "event-outbox",
        "processor",
    ]
    assert "dashboard" not in session
    assert session["request_id"] == "req-1"


def test_trace_event_normalizes_raw_repository_events():
    event = TraceEvent.from_repository_event(pending_event())

    assert event.id == "evt_foundation"
    assert event.object_id == "obj_foundation"
    assert event.owner_id == "lucas"
    assert event.status == "pending"
    assert event.detail["key"].endswith("demo.md")
    assert trace_id_for_event(event) == "trace_obj_foundation_evt_foundation"


def test_trace_list_and_detail_are_causal_not_dashboard_metrics():
    event = TraceEvent.from_repository_event(pending_event())

    trace_list = build_trace_list([event])
    assert trace_list["count"] == 1
    summary = trace_list["traces"][0]
    assert summary["status"] == "pending"
    assert summary["artifact"]["object_id"] == "obj_foundation"
    assert summary["links"]["detail"] == "/ops/traces/trace_obj_foundation_evt_foundation"
    assert "metrics" not in summary

    detail = build_trace_detail(event, owner_id="lucas")
    assert [step["id"] for step in detail["steps"]] == ["request", "payload", "object-store", "metadata", "outbox", "processor"]
    assert detail["steps"][-1]["status"] == "waiting"
    assert detail["commands"][0]["kind"] == "curl"
    assert "x-floci-user: lucas" in detail["commands"][0]["command"]


def test_trace_commands_shell_quote_owner_header_values():
    event = TraceEvent.from_repository_event({**pending_event(), "owner_id": "lucas'; rm -rf / #"})

    detail = build_trace_detail(event, owner_id="lucas'; rm -rf / #")
    command = detail["commands"][0]["command"]

    assert "x-floci-user: lucas'; rm -rf / #" not in command
    assert "'\"'\"'" in command
    assert detail["commands"][0]["argv"] == [
        "curl",
        "-X",
        "POST",
        "-H",
        "content-type: application/json",
        "-H",
        "x-floci-user: lucas'; rm -rf / #",
        "http://127.0.0.1:8080/objects",
    ]


def test_sanitized_trace_report_redacts_secret_assignments_inside_strings():
    trace = {
        "id": "trace_secret",
        "steps": [
            {
                "id": "log",
                "detail": "env AWS_SECRET_ACCESS_KEY=super-secret AWS_ACCESS_KEY_ID: AKIAFAKE123 token: abc123 password='hunter2'",
            }
        ],
        "api_key": "key-123",
        "passwd": "passwd-123",
    }

    report = build_sanitized_trace_report(trace=trace, request_id="req-secret")
    rendered = str(report)

    assert "super-secret" not in rendered
    assert "AKIAFAKE123" not in rendered
    assert "abc123" not in rendered
    assert "hunter2" not in rendered
    assert "key-123" not in rendered
    assert "passwd-123" not in rendered
    assert "AWS_SECRET_ACCESS_KEY" not in rendered
    assert "AWS_ACCESS_KEY_ID" not in rendered
    assert "token" not in rendered.lower()
    assert "api_key" not in rendered.lower()
    assert "passwd" not in rendered.lower()


def test_sanitized_trace_report_redacts_quoted_secret_values_with_spaces():
    trace = {
        "id": "trace_secret_spaces",
        "detail": "password='hunter two' api_key: \"key with spaces\" token=plain",
    }

    report = build_sanitized_trace_report(trace=trace, request_id="req-secret")
    rendered = str(report)

    assert "hunter" not in rendered
    assert "two" not in rendered
    assert "key with spaces" not in rendered
    assert "plain" not in rendered
    assert "password" not in rendered.lower()
    assert "api_key" not in rendered.lower()
    assert "token" not in rendered.lower()


def test_sanitized_trace_report_is_portfolio_ready_and_secret_safe():
    event = TraceEvent.from_repository_event(pending_event())
    trace = build_trace_detail(event, owner_id="lucas")

    report = build_sanitized_trace_report(trace=trace, request_id="req-report")

    assert report["format"] == "floci.trace-report.v1"
    assert report["request_id"] == "req-report"
    assert report["trace"]["id"] == "trace_obj_foundation_evt_foundation"
    assert report["safety"]["sanitized"] is True
    assert report["safety"]["contains_real_credentials"] is False
    assert report["reproduction"]["local_only"] is True
    rendered = str(report)
    assert "AWS_SECRET_ACCESS_KEY" not in rendered
    assert "AWS_ACCESS_KEY_ID" not in rendered
