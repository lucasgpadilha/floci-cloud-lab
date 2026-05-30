from pathlib import Path

CONSOLE_HTML = Path("app/local-cloud-console/index.html")


def html() -> str:
    return CONSOLE_HTML.read_text(encoding="utf-8")


def test_console_leads_with_trace_debugger_not_generic_dashboard():
    page = html()

    assert "Floci Studio" in page
    assert "Local workflow debugger" in page
    assert "Create broken trace" in page
    assert "Trace detail" in page
    assert "Failure reason" in page
    assert page.index("Create broken trace") < page.index("Object evidence")
    assert "Dashboard KPIs" not in page
    assert "Lightweight cloud console for local emulators" not in page


def test_console_wires_trace_workbench_endpoints():
    page = html()

    assert "/ops/demo/broken-trace" in page
    assert "/ops/traces?" in page
    assert "/ops/traces/" in page
    assert "/ops/report?trace_id=" in page
    assert "selectedTrace" in page
    assert "renderTraceDetail" in page


def test_console_surfaces_local_only_report_safety():
    page = html()

    assert "sanitized" in page
    assert "local_only" in page
    assert "uses_real_cloud" in page
    assert "allows_shell_execution" in page
    assert "Export sanitized report" in page
    assert "Copy report JSON" in page


def test_console_blocks_non_local_endpoints_and_browser_shell_execution():
    page = html()

    assert "safeLocal" in page
    assert "Blocked non-local API URL" in page
    assert "new URL" in page
    assert "parsed.hostname === '127.0.0.1'" in page
    assert "parsed.hostname === 'localhost'" in page
    assert "parsed.username" in page
    assert "parsed.password" in page
    assert "os.system" not in page
    assert "subprocess" not in page
    assert "eval(" not in page
    assert "new Function" not in page


def test_console_renders_adapter_data_without_trace_inner_html():
    page = html()

    assert "hero.innerHTML" not in page
    assert "text('p', failure.reason" in page
