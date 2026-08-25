from __future__ import annotations

import copy
from pathlib import Path

from services.simulator.contracts import Scenario
from services.simulator.data import load_simulation_facilities
from services.simulator.storage import ScenarioStore


ROOT = Path(__file__).resolve().parents[2]
STORE = ScenarioStore(ROOT / "data/scenarios/goal4a")
BASE_ID = "anyang-general-evacuation-competition"
VARIANT_ID = "anyang-general-evacuation-competition-shelter-outage"


def main() -> None:
    base = STORE.get(BASE_ID)
    # This fixed shelter carries the largest baseline assignment in the frozen
    # competition preset, so its closure produces a visible but real delta.
    shelter = next(item for item in load_simulation_facilities() if item.get("id") == "civil-defense-shelter-national:9e0a7a6e9dbd3578")
    payload = copy.deepcopy(base.to_dict())
    payload["scenario_id"] = VARIANT_ID
    payload["title"] = "안양 인접 2개 영역 + 대피소 1곳 폐쇄"
    payload["description"] = "고정 competition A/B 비교: 동일한 영향영역에서 대피소 1곳을 폐쇄한 exact what-if"
    payload["assumptions"] = [*payload.get("assumptions", []), f"A/B B는 동일 영역에서 {shelter['id']} 한 곳을 시작 시점에 폐쇄"]
    payload["facility_events"] = [{"start_minute": 0, "end_minute": base.frame_times()[-1], "facility_id": shelter["id"], "available": False, "reason": "고정 A/B demo에서 대피소 1곳 폐쇄", "provenance": "ADMIN_SCENARIO"}]
    payload["audit_log"] = []
    STORE.save(Scenario.from_dict(payload), action="goal6a-fixed-ab-preset", actor="system")
    print(VARIANT_ID, shelter["id"])


if __name__ == "__main__":
    main()
