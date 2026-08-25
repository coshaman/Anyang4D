import asyncio

import httpx

from services.api.main import app


def request(path: str) -> httpx.Response:
    async def run() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get(path)

    return asyncio.run(run())


def test_real_terrain_gate_reports_coarse_duplicate_dem_without_promoting_it():
    response = request("/api/admin/flood-readiness")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CLOSED_NOT_RELEASE_DEPENDENCY"
    assert body["native_resolution_m"] == 90
    assert body["duplicate_source_bytes"] is True
    assert body["real_level_a_authorized"] is False
    assert body["admin_scenario_authorized"] is True
    assert body["citizen_routing_authorized"] is False
    assert body["high_res_terrain_acquisition"] == "CLOSED"
    assert body["terrain_dependency_for_release"] is False
    assert "permanently closed" in body["reason"]
