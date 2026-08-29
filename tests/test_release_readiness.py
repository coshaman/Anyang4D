from services.api.main import app
import services.api.readiness as readiness


def test_release_readiness_reports_frozen_boundary_and_ready_artifacts():
    payload = next(route.endpoint() for route in app.routes if getattr(route, "path", None) == "/api/release/readiness")
    assert payload["status"] == "READY"
    assert payload["mandatory_checks"]["population_loaded"]["total_population"] == 562143
    assert payload["ai_decision"].endswith("DEMO_ONLY")
    assert payload["frozen_boundary"]["final_terrain_class"] == "TERRAIN_C"


def test_readiness_payload_is_cached_between_calls(monkeypatch):
    readiness.readiness_payload.cache_clear()
    calls = 0
    original = readiness.load_population_demand

    def counted_loader():
        nonlocal calls
        calls += 1
        return original()

    monkeypatch.setattr(readiness, "load_population_demand", counted_loader)
    readiness.readiness_payload()
    readiness.readiness_payload()
    assert calls == 1
