from pathlib import Path

from services.api.goal5a import _SCENARIOS
from services.api.main import app
import asyncio
import httpx


def test_goal5a_status_is_fail_closed_before_model_bundle():
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get("/api/admin/goal5a/status")
    response = asyncio.run(run())
    assert response.status_code == 200
    assert response.json()["exact_reference_available"] is True


def test_goal5a_screening_endpoint_is_admin_only_namespace():
    paths = set(app.openapi()["paths"])
    assert "/api/admin/goal5a/screen" not in {path for path in paths if not path.startswith("/api/admin/goal5a")}
    assert "/api/admin/goal5a/screen" in paths
