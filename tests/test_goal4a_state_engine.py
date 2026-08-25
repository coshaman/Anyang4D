from datetime import datetime, timedelta, timezone

import pytest

from services.simulator.contracts import DemandUnit, Scenario
from services.simulator.engine import resolve_frame


def _scenario() -> Scenario:
    start = datetime(2026, 8, 22, 0, 0, tzinfo=timezone.utc)
    return Scenario.from_dict({
        "scenario_id": "fixture",
        "title": "훈련/가정 시나리오",
        "disaster_type": "FLOOD",
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(minutes=20)).isoformat(),
        "timestep_minutes": 10,
        "provenance": "ADMIN_SCENARIO",
        "description": "fixture",
        "assumptions": ["가정 침수영역은 실제 침수심이 아님"],
        "hazard_keyframes": [
            {"time": 0, "geometry": {"kind": "polygon", "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}, "label": "t0"},
            {"time": 10, "geometry": {"kind": "polygon", "coordinates": [[[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]]]}, "label": "t1"},
        ],
        "road_closure_events": [{"start_minute": 10, "end_minute": 20, "edge_ids": ["1-2"], "reason": "시나리오에서 통행 제한으로 설정된 도로", "provenance": "ADMIN_SCENARIO"}],
        "facility_events": [{"start_minute": 20, "end_minute": 30, "facility_id": "s1", "available": False, "reason": "훈련 시나리오 시설 폐쇄", "provenance": "ADMIN_SCENARIO"}],
        "capacity_overrides": [{"start_minute": 10, "end_minute": 30, "facility_id": "s1", "capacity": 2, "reason": "훈련 시나리오 용량 조정", "provenance": "ADMIN_SCENARIO"}],
        "demand_units": [{"demand_id": "d1", "label": "시뮬레이션 수요 A", "latitude": 0.0, "longitude": 0.0, "population": 3, "provenance": "ADMIN_SCENARIO", "source_period": None}],
    })


def test_scenario_serialization_round_trip_and_stepwise_keyframe():
    scenario = _scenario()
    clone = Scenario.from_dict(scenario.to_dict())
    assert clone.to_dict() == scenario.to_dict()
    frame0 = resolve_frame(scenario, 0, [], [])
    frame1 = resolve_frame(scenario, 10, [], [])
    assert frame0.hazard_geometry != frame1.hazard_geometry
    assert frame0.time_minute == 0
    assert frame1.time_minute == 10


def test_scenario_rejects_unsupported_disaster_type():
    with pytest.raises(ValueError, match="disaster_type"):
        Scenario.from_dict({**_scenario().to_dict(), "disaster_type": "UNKNOWN"})


def test_resource_event_changes_frame_state_and_replays_deterministically():
    scenario = Scenario.from_dict({**_scenario().to_dict(), "resource_events": [{"start_minute": 10, "end_minute": 20, "resource_id": "water-1", "available": False, "reason": "관리자 훈련 폐쇄", "provenance": "ADMIN_SCENARIO"}]})
    resources = [{"id": "water-1", "category": "EMERGENCY_WATER", "provenance": "OFFICIAL"}]
    open_frame = resolve_frame(scenario, 0, [], [], resources)
    closed_frame = resolve_frame(scenario, 10, [], [], resources)
    assert open_frame.resources["water-1"].available is True
    assert closed_frame.resources["water-1"].available is False
    assert closed_frame.resources == resolve_frame(scenario, 10, [], [], resources).resources
