import asyncio

import httpx

from services.api.main import app


def request(path: str) -> httpx.Response:
    async def run() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get(path)

    return asyncio.run(run())


def test_optional_modules_have_evidence_backed_terminal_statuses():
    response = request("/api/admin/optional-modules")
    assert response.status_code == 200
    items = {item["module"]: item for item in response.json()["items"]}
    assert {"TerraMind", "xBD-S12", "MapAnything", "JuPedSim"} == set(items)
    assert all(item["status"] in {"INTEGRATED", "REJECTED"} for item in items.values())
    assert all(item["status"] == "REJECTED" for item in items.values())
    assert all(item["evidence"] for item in items.values())
    assert all(item["citizen_guidance_authorized"] is False for item in items.values())


def test_optional_module_detail_is_available():
    response = request("/api/admin/optional-modules/MapAnything")
    assert response.status_code == 200
    body = response.json()
    assert body["license"] == "Apache-2.0"
    assert "legally collected imagery" in body["reason"]

