import asyncio

import httpx

from services.api.main import app




def get(path: str) -> httpx.Response:
    async def request() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get(path)

    return asyncio.run(request())


def test_foundation_status_exposes_real_provenance_contract():
    response = get("/api/foundation")

    assert response.status_code == 200
    body = response.json()
    assert body["provenance"] == "OFFICIAL"
    assert body["fixture"] is False
    assert body["counts"] == {"CIVIL_DEFENSE_SHELTER": 231, "EMERGENCY_WATER": 71, "AED": 305}
    assert set(body["allowed_provenance"]) == {
        "OFFICIAL",
        "SIMULATED",
        "OBSERVED_AI",
        "STALE_OR_UNKNOWN",
    }


def test_facilities_are_real_data_with_official_provenance():
    response = get("/api/facilities?type=civil_defense")

    assert response.status_code == 200
    body = response.json()
    assert body["provenance"] == "OFFICIAL"
    assert body["fixture"] is False
    assert len(body["items"]) == 231
    assert body["items"][0]["source_dataset_id"] == "civil-defense-shelter-national"
