from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .contracts import Scenario


def _base(scenario_id: str, title: str, disaster_type: str, demand_units: list[dict[str, Any]]) -> dict[str, Any]:
    start = datetime(2026, 8, 22, 0, 0, tzinfo=timezone.utc)
    return {
        "scenario_id": scenario_id, "title": title, "disaster_type": disaster_type,
        "start_time": start.isoformat(), "end_time": (start + timedelta(minutes=30)).isoformat(),
        "timestep_minutes": 10, "provenance": "ADMIN_SCENARIO", "description": "훈련/가정 시나리오",
        "assumptions": ["가정 hazard geometry는 실제 재난 예측이나 침수심이 아님", "공식 행정동 주민등록 인구 총량을 사용하며 좌표는 SIMULATED_SPATIAL_ALLOCATION demo anchor"],
        "hazard_keyframes": [], "road_closure_events": [], "facility_events": [], "capacity_overrides": [], "resource_events": [],
        "affected_demand_ids": [], "evacuation_fraction": 1.0, "affected_demand_rule": "HAZARD_CONTAINMENT_OR_EXPLICIT_SELECTION",
        "demand_units": demand_units,
    }


def build_presets(facilities: list[dict[str, Any]], demand_units: list[dict[str, Any]] | None = None) -> list[Scenario]:
    demand_units = demand_units or [{"demand_id": "admin-demand-fallback", "label": "행정수요 가정", "latitude": 37.395, "longitude": 126.95, "population": 280, "provenance": "ADMIN_SCENARIO", "source_period": None}]
    shelters = [item for item in facilities if item.get("category") == "CIVIL_DEFENSE_SHELTER" and item.get("latitude") is not None and item.get("longitude") is not None]
    first_shelter = shelters[0]["id"] if shelters else None
    flood = _base("anyang-flood-style-admin", "안양 가정 침수영역 확장", "FLOOD", demand_units)
    flood["hazard_keyframes"] = [
        {"time": 0, "label": "초기 가정 침수영역", "geometry": {"kind": "polygon", "coordinates": [[[126.925, 37.375], [126.945, 37.375], [126.945, 37.39], [126.925, 37.39], [126.925, 37.375]]]}},
        {"time": 20, "label": "확장 가정 침수영역", "geometry": {"kind": "polygon", "coordinates": [[[126.925, 37.375], [126.955, 37.375], [126.955, 37.4], [126.925, 37.4], [126.925, 37.375]]]}},
    ]
    earthquake = _base("anyang-earthquake-training", "안양 지진 대피 훈련", "EARTHQUAKE", demand_units)
    earthquake["assumptions"].append("지진 옥외대피장소 원자료가 없어 해당 시설 유형은 비활성")
    earthquake["road_closure_events"] = [{"start_minute": 10, "end_minute": 30, "edge_ids": [], "reason": "관리자가 설정한 지진 훈련 통행 제한 없음(시설 eligibility만 확인)", "provenance": "ADMIN_SCENARIO"}]
    earthquake["affected_demand_ids"] = [unit["demand_id"] for unit in demand_units]
    earthquake["affected_demand_rule"] = "EXPLICIT_DEMAND_SELECTION_SCHEMA_DEMO"
    fire = _base("anyang-fire-exclusion-training", "안양 화재 제외영역 훈련", "FIRE", demand_units)
    fire["hazard_keyframes"] = [{"time": 0, "label": "화재 가정 제외영역", "geometry": {"kind": "point_radius", "center": [126.95, 37.4], "radius_m": 600}}]
    outage = _base("anyang-civil-defense-outage", "민방위 대피시설 일부 폐쇄", "CIVIL_DEFENSE", demand_units)
    if first_shelter:
        outage["facility_events"] = [{"start_minute": 10, "end_minute": 30, "facility_id": first_shelter, "available": False, "reason": "훈련 시나리오에서 대피시설 폐쇄", "provenance": "ADMIN_SCENARIO"}]
    general = _base("anyang-general-evacuation-competition", "안양 인접 2개 영역 대피 경쟁", "GENERAL_EVACUATION", demand_units)
    general["hazard_keyframes"] = [{"time": 0, "label": "첫 번째 가정 영향영역", "geometry": {"kind": "polygon", "coordinates": [[[126.9, 37.35], [126.94, 37.35], [126.94, 37.39], [126.9, 37.39], [126.9, 37.35]]]}}, {"time": 20, "label": "두 번째 인접 가정 영향영역 추가", "geometry": {"kind": "multipolygon", "coordinates": [[[[126.9, 37.35], [126.94, 37.35], [126.94, 37.39], [126.9, 37.39], [126.9, 37.35]]], [[[126.94, 37.35], [126.99, 37.35], [126.99, 37.39], [126.94, 37.39], [126.94, 37.35]]]]}}]
    v2_demo = _base("anyang-v2-four-state-demo", "안양 4D 네 상태 시각화 데모", "GENERAL_EVACUATION", demand_units)
    v2_demo["hazard_keyframes"] = [
        {"time": 0, "label": "0분 · 초기 영향영역", "geometry": {"kind": "polygon", "coordinates": [[[126.9, 37.375], [126.945, 37.375], [126.945, 37.39], [126.9, 37.39], [126.9, 37.375]]]}},
        {"time": 10, "label": "10분 · 동쪽으로 확장", "geometry": {"kind": "polygon", "coordinates": [[[126.9, 37.375], [126.96, 37.375], [126.96, 37.395], [126.9, 37.395], [126.9, 37.375]]]}},
        {"time": 20, "label": "20분 · 북쪽 영역 추가", "geometry": {"kind": "multipolygon", "coordinates": [[[[126.9, 37.375], [126.96, 37.375], [126.96, 37.395], [126.9, 37.395], [126.9, 37.375]]], [[[126.94, 37.395], [126.975, 37.395], [126.975, 37.42], [126.94, 37.42], [126.94, 37.395]]]]}},
        {"time": 30, "label": "30분 · 넓은 최종 영향영역", "geometry": {"kind": "polygon", "coordinates": [[[126.91, 37.365], [126.985, 37.365], [126.985, 37.425], [126.91, 37.425], [126.91, 37.365]]]}},
    ]
    if first_shelter:
        v2_demo["facility_events"] = [{"start_minute": 20, "end_minute": 31, "facility_id": first_shelter, "available": False, "reason": "4D 데모에서 시설 상태 변화", "provenance": "ADMIN_SCENARIO"}]
    return [Scenario.from_dict(item) for item in [flood, earthquake, fire, outage, general, v2_demo]]
