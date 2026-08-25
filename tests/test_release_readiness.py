from services.api.main import app


def test_release_readiness_reports_frozen_boundary_and_ready_artifacts():
    payload = next(route.endpoint() for route in app.routes if getattr(route, "path", None) == "/api/release/readiness")
    assert payload["status"] == "READY"
    assert payload["mandatory_checks"]["population_loaded"]["total_population"] == 562143
    assert payload["ai_decision"].endswith("DEMO_ONLY")
    assert payload["frozen_boundary"]["final_terrain_class"] == "TERRAIN_C"
