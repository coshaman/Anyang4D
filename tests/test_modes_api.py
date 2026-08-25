import asyncio

import httpx

from services.api.main import app


def request(path: str, **kwargs) -> httpx.Response:
    async def run() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get(path, **kwargs)

    return asyncio.run(run())


def test_mode_contracts_are_explicit_about_sources_and_claim_boundaries():
    response = request("/api/admin/modes")
    assert response.status_code == 200
    body = response.json()
    modes = {item["mode"]: item for item in body["items"]}
    assert {"FLOOD", "EARTHQUAKE", "FIRE", "CIVIL_DEFENSE", "AED"} <= modes.keys()
    assert modes["FLOOD"]["source_status"] == "ADMIN_SCENARIO"
    assert "terrain-derived flood depth" in modes["FLOOD"]["unsupported_claims"]
    assert modes["EARTHQUAKE"]["source_status"] == "HUMAN_AUTH_REQUIRED"
    assert modes["AED"]["first_action"] == "119"


def test_mode_contract_can_be_filtered():
    response = request("/api/admin/modes/FIRE")
    assert response.status_code == 200
    assert response.json()["mode"] == "FIRE"
    assert response.json()["citizen_guidance_authorized"] is False

