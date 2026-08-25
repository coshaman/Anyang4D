from services.terrain.rst import inspect_rst_backend


def test_rst_adapter_reports_explicit_environment_status():
    result = inspect_rst_backend()
    assert result["status"] in {"AVAILABLE_NOT_RUN", "METHOD_B_NOT_RUN"}
    assert "reason" in result
