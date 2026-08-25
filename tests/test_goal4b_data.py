import json
from pathlib import Path

from services.api.goal4a import STORE, _ensure_presets, _frame_payload, clear_computation_caches
from services.api.main import app
import asyncio
import httpx
from services.simulator.data import load_local_resource_context

ROOT = Path(__file__).resolve().parents[1]


def test_goal4b_local_sources_are_current_and_explicitly_provenanced():
    shelters = json.loads((ROOT / "data/processed/anyang_local_shelters.json").read_text(encoding="utf-8"))
    assert shelters["record_count"] == 224
    assert all(item["provenance"] == "ANYANG_LOCAL_OFFICIAL" for item in shelters["items"])
    resources = load_local_resource_context()
    assert len(resources["water"]) == 46
    assert len(resources["flood_response_inventory"]) == 33
    assert all(item["provenance"] == "ANYANG_LOCAL_OFFICIAL" for item in resources["water"])
    assert all(item["capacity_role"] == "RESPONSE_RESOURCE_CAPACITY" for item in resources["water"])


def test_goal4b_crosswalk_is_conservative_and_unmerged():
    crosswalk = json.loads((ROOT / "artifacts/evals/data/goal4b-shelter-crosswalk.json").read_text(encoding="utf-8"))
    assert (crosswalk["local_count"], crosswalk["national_count"]) == (224, 231)
    assert crosswalk["counts"]["AMBIGUOUS"] == 0
    assert all(match["chosen_operational_value"] == "PRESERVE_BOTH_SOURCES_UNMERGED" for match in crosswalk["matches"] if match["local"] and match["national"])


def test_goal4b_participation_is_deterministic_and_conserves_demand():
    _ensure_presets()
    scenario = STORE.get("anyang-flood-style-admin")
    clear_computation_caches()
    full = _frame_payload(scenario, 20)
    half = scenario.from_dict(scenario.to_dict() | {"scenario_id": "test-half", "evacuation_fraction": 0.5})
    half_frame = _frame_payload(half, 20)
    assert full["assignment"]["total_population"] == 562143
    assert half_frame["assignment"]["affected_population"] == full["assignment"]["affected_population"]
    assert half_frame["assignment"]["evacuation_demand"] <= full["assignment"]["evacuation_demand"]
    assert half_frame["assignment"]["assigned"] + half_frame["assignment"]["unserved"] == half_frame["assignment"]["evacuation_demand"]


def test_goal4b_cached_frame_is_semantically_equal():
    _ensure_presets()
    scenario = STORE.get("anyang-flood-style-admin")
    clear_computation_caches()
    first = _frame_payload(scenario, 20)
    second = _frame_payload(scenario, 20)
    assert second["computation_status"] == "CACHED"
    assert {key: value for key, value in first.items() if key != "computation_status"} == {key: value for key, value in second.items() if key != "computation_status"}


def test_goal4b_compilation_endpoint_reports_indexed_states():
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post("/api/admin/goal4a/scenarios/anyang-general-evacuation-competition/compile")
    response = asyncio.run(run())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CACHED"
    assert body["frame_count"] == 4
    assert body["unique_state_count"] >= 1
