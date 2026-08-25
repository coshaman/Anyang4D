import asyncio

import httpx

from services.api.main import app


def request(method: str, path: str, **kwargs) -> httpx.Response:
    async def run() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(run())


def test_real_foundation_is_not_fixture_and_reports_counts():
    response = request("GET", "/api/foundation")
    assert response.status_code == 200
    body = response.json()
    assert body["provenance"] == "OFFICIAL"
    assert body["fixture"] is False
    assert body["counts"] == {"CIVIL_DEFENSE_SHELTER": 231, "EMERGENCY_WATER": 71, "AED": 305}


def test_facilities_filter_by_real_category_and_source_availability():
    response = request("GET", "/api/facilities", params={"type": "AED"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 305
    assert body["items"][0]["provenance"] == "OFFICIAL"
    assert body["source_availability"]["EARTHQUAKE_OUTDOOR_SHELTER"]["status"] == "HUMAN_AUTH_REQUIRED"


def test_local_shelter_context_is_queryable_without_merging_national_records():
    response = request("GET", "/api/facilities", params={"type": "local_shelter"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 224
    assert all(item["provenance"] == "OFFICIAL" for item in body["items"])
    assert all(item["source_provenance"] == "ANYANG_LOCAL_OFFICIAL" for item in body["items"])
    assert {item["source_dataset_id"] for item in body["items"]} == {"anyang-local-civil-defense-shelter-board"}


def test_route_endpoint_returns_baseline_route_shape():
    response = request("POST", "/api/routes", json={"origin": {"latitude": 37.390, "longitude": 126.950}, "destination": {"latitude": 37.3905, "longitude": 126.9505}})
    assert response.status_code == 200
    body = response.json()
    assert body["distance_m"] > 0
    assert body["hazard_exposure"] is None
    assert body["provenance"] == "OFFICIAL"
