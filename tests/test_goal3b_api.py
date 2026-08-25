import asyncio

import httpx

from services.api.main import app


def request(path: str) -> httpx.Response:
    async def run() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get(path)

    return asyncio.run(run())


def test_internal_lab_lists_only_explicit_non_citizen_scenarios():
    response = request("/api/internal/simulations")
    assert response.status_code == 200
    body = response.json()
    assert all(item["provenance"] in {"SYNTHETIC", "BENCHMARK"} for item in body["items"])


def test_internal_lab_exposes_frame_metadata_and_fidelity_warning():
    scenario = request("/api/internal/simulations/anyang-demo-synthetic")
    assert scenario.status_code == 200
    body = scenario.json()
    assert body["fidelity_level"] == "A"
    assert body["warning"]
    frame = request("/api/internal/simulations/anyang-demo-synthetic/frames/0")
    assert frame.status_code == 200
    assert frame.json()["provenance"] == "SYNTHETIC"
