import asyncio

import httpx

from services.api.main import app
from services.api.goal4a import _roads_cached


def request(method: str, path: str, **kwargs):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.request(method, path, **kwargs)
    return asyncio.run(run())


def test_goal4a_lists_real_data_backed_admin_presets():
    response = request("GET", "/api/admin/goal4a/scenarios")
    assert response.status_code == 200
    ids = {item["scenario_id"] for item in response.json()["items"]}
    assert {"anyang-flood-style-admin", "anyang-earthquake-training", "anyang-fire-exclusion-training", "anyang-civil-defense-outage"} <= ids


def test_goal4a_frame_changes_with_timeline_and_stays_training_only():
    first = request("GET", "/api/admin/goal4a/scenarios/anyang-flood-style-admin/frames/0")
    later = request("GET", "/api/admin/goal4a/scenarios/anyang-flood-style-admin/frames/20")
    assert first.status_code == 200
    assert later.status_code == 200
    assert first.json()["hazard"]["geometry"] != later.json()["hazard"]["geometry"]
    assert later.json()["terrain_authorized"] is False
    assert later.json()["citizen_guidance_authorized"] is False
    assert later.json()["assignment"]["total_population"] == 562143
    assert later.json()["assignment"]["affected_population"] > 0
    assert later.json()["assignment"]["assigned"] + later.json()["assignment"]["unserved"] == later.json()["assignment"]["evacuation_demand"]
    assert "resources" in later.json()


def test_scenario_export_contains_caveats_and_frame():
    response = request("GET", "/api/admin/goal4a/scenarios/anyang-flood-style-admin/export?time_minute=20")
    assert response.status_code == 200
    body = response.json()
    assert body["export_type"] == "GOAL4A_SCENARIO_SUMMARY"
    assert body["frame"]["time_minute"] == 20
    assert body["caveats"]


def test_nearest_road_selection_resolves_map_click_without_edge_id_input():
    road = _roads_cached()[0]
    midpoint = [(road["a"][0] + road["b"][0]) / 2, (road["a"][1] + road["b"][1]) / 2]
    response = request("POST", "/api/admin/goal4a/roads/nearest", json={"longitude": midpoint[0], "latitude": midpoint[1]})
    assert response.status_code == 200
    assert response.json()["edge_id"] == road["edge_id"]
    assert response.json()["selection"] == "MAP_CLICK_NEAREST_OSM_EDGE"
