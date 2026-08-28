"""Production-parity contract tests; run against a running built container."""
from __future__ import annotations

import os

import pytest
import requests


BASE = os.environ.get("SAFE_TWIN_PRODUCTION_URL", "http://127.0.0.1:8080").rstrip("/")


def get(path: str):
    return requests.get(BASE + path, timeout=15)


@pytest.mark.production_container
def test_production_container_core_contract():
    if "SAFE_TWIN_PRODUCTION_URL" not in os.environ:
        pytest.skip("set SAFE_TWIN_PRODUCTION_URL to run against a built production container")
    assert get("/healthz").status_code == 200
    assert get("/readyz").status_code == 200
    readiness = get("/api/release/readiness")
    assert readiness.status_code == 200
    assert all(check["ready"] for check in readiness.json()["mandatory_checks"].values())

    scenarios = get("/api/admin/goal4a/scenarios")
    assert scenarios.status_code == 200
    assert {item["scenario_id"] for item in scenarios.json()["items"]} >= {"anyang-general-evacuation-competition", "anyang-flood-style-admin"}

    resources = get("/api/admin/goal4a/resources")
    assert resources.status_code == 200
    assert resources.json()["count"] > 0

    aed = get("/api/facilities?type=aed")
    assert aed.status_code == 200
    assert len(aed.json()["items"]) == 305

    route = requests.post(BASE + "/api/routes", json={"origin": {"latitude": 37.390, "longitude": 126.950}, "destination": {"latitude": 37.3905, "longitude": 126.9505}}, timeout=30)
    assert route.status_code == 200
    assert len(route.json()["geometry"]) > 1
