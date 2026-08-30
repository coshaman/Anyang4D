from __future__ import annotations

import json
import copy
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from services.simulator.contracts import Scenario
from services.simulator.data import load_local_resource_context, load_population_demand, load_simulation_facilities, load_simulation_graph
from services.simulator.engine import build_training_route, clear_engine_caches, derive_evacuation_demand, resolve_frame, solve_assignment
from services.simulator.presets import build_presets
from services.simulator.storage import ScenarioStore

ROOT = Path(__file__).resolve().parents[2]
STORE = ScenarioStore(ROOT / "data/scenarios/goal4a")
router = APIRouter(prefix="/api/admin/goal4a", tags=["goal4a-admin-simulator"])
_STATE_PAYLOAD_CACHE: dict[str, dict[str, Any]] = {}


def clear_computation_caches() -> None:
    _STATE_PAYLOAD_CACHE.clear()
    _frame_payload_cached.cache_clear()
    clear_engine_caches()


def _ensure_presets() -> None:
    demand = load_population_demand()
    expected = {scenario.scenario_id: scenario for scenario in build_presets(load_simulation_facilities(), demand)}
    existing = {scenario.scenario_id: scenario for scenario in STORE.list()}
    for scenario_id, preset in expected.items():
        current = existing.get(scenario_id)
        # Migrate untouched first-generation presets to the official population
        # source without overwriting later administrator edits.
        if current is None:
            STORE.save(preset, action="preset-created", actor="system")
        elif set(entry.get("action") for entry in current.audit_log) <= {"preset-created", "official-population-migration"} and (sum(unit.population for unit in current.demand_units) != sum(unit["population"] for unit in demand) or any(event.facility_id not in {item["id"] for item in _facilities()} for event in current.facility_events)):
            current.demand_units = preset.demand_units
            current.assumptions = preset.assumptions
            current.facility_events = preset.facility_events
            STORE.save(current, action="official-population-migration", actor="system")


@lru_cache(maxsize=1)
def _facilities() -> list[dict[str, Any]]:
    return load_simulation_facilities()


@lru_cache(maxsize=1)
def _graph():
    return load_simulation_graph()


@lru_cache(maxsize=1)
def _roads_cached() -> tuple[dict[str, Any], ...]:
    graph, coords = _graph()
    return tuple({"edge_id": data.get("edge_id", f"{first}-{second}"), "a": (coords[first][1], coords[first][0]), "b": (coords[second][1], coords[second][0])} for first, second, data in graph.edges(data=True))


def _roads(graph, coords) -> list[dict[str, Any]]:
    return _roads_cached()


def _resource_payload() -> list[dict[str, Any]]:
    national = [facility for facility in _facilities() if facility.get("category") == "EMERGENCY_WATER"]
    local = []
    for item in load_local_resource_context()["water"]:
        local.append({
            "id": item["resource_id"],
            "source_dataset_id": "anyang-local-emergency-water",
            "name": item["name"],
            "category": "RESPONSE_RESOURCE_CAPACITY",
            "address": item["address"],
            "capacity_tons_per_day": item["capacity_tons_per_day"],
            "available_persons": item["available_persons"],
            "provenance": item["provenance"],
            "source_provenance": "ANYANG_LOCAL_OFFICIAL",
            "capacity_role": "RESPONSE_RESOURCE_CAPACITY",
        })
    for item in national:
        item.setdefault("source_provenance", "NATIONAL_OFFICIAL_FILTERED_ANYANG")
    return national + local


def _frame_payload(scenario: Scenario, time_minute: int) -> dict[str, Any]:
    signature = json.dumps(scenario.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    before = _frame_payload_cached.cache_info().hits
    result = _frame_payload_cached(signature, time_minute)
    if _frame_payload_cached.cache_info().hits > before:
        result = copy.deepcopy(result)
        result["computation_status"] = "CACHED"
    return result


@lru_cache(maxsize=64)
def _frame_payload_cached(scenario_json: str, time_minute: int) -> dict[str, Any]:
    """Cache deterministic frame results; the scenario JSON makes edits invalidate safely."""
    scenario = Scenario.from_dict(json.loads(scenario_json))
    graph, coords = _graph()
    facilities = _facilities()
    resources = _resource_payload()
    frame = resolve_frame(scenario, time_minute, _roads(graph, coords), facilities, resources)
    state_signature = json.dumps({
        "roads_closed": [(key, value.reasons) for key, value in sorted(frame.roads.items()) if not value.available],
        "facilities": [(key, value.available, value.effective_capacity) for key, value in sorted(frame.facilities.items())],
        "resources": [(key, value.available) for key, value in sorted(frame.resources.items())],
        "hazard": frame.hazard_geometry,
        "demand": [(unit.demand_id, unit.population) for unit in scenario.demand_units],
        "participation": scenario.evacuation_fraction,
        "eligible": sorted(scenario.eligible_facility_ids),
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    cached = _STATE_PAYLOAD_CACHE.get(state_signature)
    if cached is not None:
        reused = copy.deepcopy(cached)
        reused["scenario_id"] = scenario.scenario_id
        reused["time_minute"] = time_minute
        reused["hazard"]["label"] = frame.hazard_label
        reused["computation_status"] = "CACHED"
        return reused
    evacuation_units, demand_meta = derive_evacuation_demand(frame, scenario, scenario.demand_units)
    assignment = solve_assignment(frame, scenario, evacuation_units, facilities, graph, coords)
    assignment.update(demand_meta)
    assignment["assignment_cost"] = round(float(assignment["average_assigned_travel_distance_m"] or 0) * float(assignment["assigned"]), 1)
    road_by_id = {str(road["edge_id"]): road for road in _roads(graph, coords)}
    changed_roads = [state.__dict__ | {"a": road_by_id[state.edge_id]["a"], "b": road_by_id[state.edge_id]["b"]} for state in frame.roads.values() if not state.available and state.edge_id in road_by_id]
    facility_states = [state.__dict__ | {"load": assignment["facility_load"].get(state.facility_id, 0)} for state in frame.facilities.values() if state.facility_id in assignment["facility_load"] or not state.available]
    demand_by_id = {unit.demand_id: unit for unit in evacuation_units}
    facility_by_id = {str(item["id"]): item for item in facilities}
    evacuation_flow = []
    for item in assignment["assignments"]:
        demand = demand_by_id.get(item["demand_id"])
        facility = facility_by_id.get(item["facility_id"])
        if demand is None or facility is None or facility.get("latitude") is None or facility.get("longitude") is None:
            continue
        capacity = max(1, int(frame.facilities[item["facility_id"]].effective_capacity))
        evacuation_flow.append({
            "demand_node_id": item["demand_id"],
            "shelter_id": item["facility_id"],
            "assigned_demand": item["assigned"],
            "load_ratio": round(assignment["facility_load"].get(item["facility_id"], 0) / capacity, 4),
            "geometry": {"type": "LineString", "coordinates": [[demand.longitude, demand.latitude], [facility["longitude"], facility["latitude"]]]},
        })
    available_shelters = sum(1 for facility in facilities if facility.get("category") == "CIVIL_DEFENSE_SHELTER" and frame.facilities.get(facility["id"]) and frame.facilities[facility["id"]].available)
    payload = {"scenario_id": scenario.scenario_id, "time_minute": time_minute, "hazard": {"geometry": frame.hazard_geometry, "label": frame.hazard_label, "provenance": scenario.provenance}, "roads": {"changed_count": len(changed_roads), "changed": changed_roads}, "facilities": facility_states, "evacuation_flow": evacuation_flow, "available_shelter_count": available_shelters, "overloaded_shelter_count": len(assignment["overloaded_facilities"]), "resources": [state.__dict__ for state in frame.resources.values()], "assignment": assignment, "demand_provenance": sorted({unit.provenance for unit in scenario.demand_units}), "terrain_authorized": False, "citizen_guidance_authorized": False, "computation_state_signature": state_signature, "computation_status": "READY"}
    if len(_STATE_PAYLOAD_CACHE) >= 128:
        _STATE_PAYLOAD_CACHE.pop(next(iter(_STATE_PAYLOAD_CACHE)))
    _STATE_PAYLOAD_CACHE[state_signature] = copy.deepcopy(payload)
    return payload


@router.get("/scenarios")
def list_scenarios() -> dict[str, Any]:
    _ensure_presets()
    return {"items": [scenario.to_dict() | {"frame_times": scenario.frame_times()} for scenario in STORE.list()]}


@router.get("/resources")
def resources() -> dict[str, Any]:
    """Official emergency-water and response-resource context; not evacuation capacity."""
    items = _resource_payload()
    return {"items": items, "count": len(items), "capacity_authorized": True, "evacuation_capacity_authorized": False, "provenance": "OFFICIAL", "source_provenance": "NATIONAL_OFFICIAL_FILTERED_ANYANG + ANYANG_LOCAL_OFFICIAL", "note": "지역 급수시설의 공식 급수용량·사용가능인원은 RESPONSE_RESOURCE_CAPACITY로만 제공하며 대피소 수용량으로 사용하지 않음"}


@router.get("/resources/inventory")
def resource_inventory() -> dict[str, Any]:
    context = load_local_resource_context()["flood_response_inventory"]
    return {"items": context, "count": len(context), "provenance": "ANYANG_LOCAL_OFFICIAL", "dispatch_optimization_authorized": False}


@router.post("/roads/nearest")
def nearest_road(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        longitude, latitude = float(payload["longitude"]), float(payload["latitude"])
        def distance(road: dict[str, Any]) -> float:
            ax, ay = road["a"]; bx, by = road["b"]
            dx, dy = bx - ax, by - ay
            denominator = dx * dx + dy * dy
            t = max(0.0, min(1.0, ((longitude - ax) * dx + (latitude - ay) * dy) / denominator)) if denominator else 0.0
            return math.hypot(longitude - (ax + t * dx), latitude - (ay + t * dy))
        road = min(_roads_cached(), key=distance)
        return {"edge_id": str(road["edge_id"]), "a": road["a"], "b": road["b"], "selection": "MAP_CLICK_NEAREST_OSM_EDGE"}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="지도 좌표가 필요합니다.") from exc


@router.get("/scenarios/{scenario_id}/export")
def export_scenario(scenario_id: str, time_minute: int = 0) -> dict[str, Any]:
    _ensure_presets()
    try:
        scenario = STORE.get(scenario_id)
        frame = _frame_payload(scenario, time_minute)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="scenario not found") from exc
    return {"export_type": "GOAL4A_SCENARIO_SUMMARY", "scenario": scenario.to_dict(), "frame": frame, "caveats": ["행정 훈련/가정 시나리오이며 공식 비상계획이 아님", "지형 파생 침수심·시민 emergency routing 미사용"]}


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str) -> dict[str, Any]:
    _ensure_presets()
    try:
        scenario = STORE.get(scenario_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="scenario not found") from exc
    return scenario.to_dict() | {"frame_times": scenario.frame_times()}


@router.post("/scenarios")
def save_scenario(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        scenario = Scenario.from_dict(payload)
        STORE.save(scenario, action="save", actor="admin")
        return scenario.to_dict()
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/scenarios/{scenario_id}/duplicate")
def duplicate_scenario(scenario_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return STORE.duplicate(scenario_id, str(payload["new_scenario_id"])).to_dict()
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/scenarios/{scenario_id}/frames/{time_minute}")
def scenario_frame(scenario_id: str, time_minute: int) -> dict[str, Any]:
    _ensure_presets()
    try:
        scenario = STORE.get(scenario_id)
        return _frame_payload(scenario, time_minute)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="scenario not found") from exc
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/scenarios/{scenario_id}/compile")
def compile_scenario(scenario_id: str) -> dict[str, Any]:
    _ensure_presets()
    try:
        scenario = STORE.get(scenario_id)
        started = __import__("time").perf_counter()
        frames = [_frame_payload(scenario, minute) for minute in scenario.frame_times()]
        unique_states = len({frame["computation_state_signature"] for frame in frames})
        elapsed = (__import__("time").perf_counter() - started) * 1000
        return {"scenario_id": scenario_id, "status": "CACHED", "frame_count": len(frames), "unique_state_count": unique_states, "elapsed_ms": round(elapsed, 2), "frame_times": scenario.frame_times()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="scenario not found") from exc
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/compare")
def compare_scenarios(payload: dict[str, Any]) -> dict[str, Any]:
    _ensure_presets()
    try:
        left = STORE.get(str(payload["scenario_a"]))
        right = STORE.get(str(payload["scenario_b"]))
        time_minute = int(payload.get("time_minute", 0))
        left_frame, right_frame = _frame_payload(left, time_minute), _frame_payload(right, time_minute)
        metrics = ["affected_population", "evacuation_demand", "assigned", "unserved", "reachable_population", "total_demand", "average_assigned_travel_distance_m", "assignment_cost"]
        delta = {metric: (right_frame["assignment"][metric] or 0) - (left_frame["assignment"][metric] or 0) for metric in metrics}
        delta.update({"changed_roads": right_frame["roads"]["changed_count"] - left_frame["roads"]["changed_count"], "available_shelters": right_frame["available_shelter_count"] - left_frame["available_shelter_count"], "overloaded_shelters": right_frame["overloaded_shelter_count"] - left_frame["overloaded_shelter_count"]})
        why: list[str] = []
        if delta["changed_roads"]:
            why.append(f"B 시나리오의 통행 제한 도로가 {delta['changed_roads']:+d}개 변했습니다.")
        if delta["available_shelters"]:
            why.append(f"가용 대피소가 {delta['available_shelters']:+d}곳 변했습니다.")
        if delta["evacuation_demand"]:
            why.append(f"영향 영역/참여율 가정으로 대피 수요가 {delta['evacuation_demand']:+,}명 변했습니다.")
        if delta["unserved"]:
            why.append(f"도로·시설 상태 변화의 결과 미배정 수요가 {delta['unserved']:+,}명 변했습니다.")
        if not why:
            why.append("비교 시점의 계산 상태가 동일하여 결과 차이가 없습니다.")
        return {"scenario_a": left_frame, "scenario_b": right_frame, "delta_b_minus_a": delta, "why": why, "causal_inputs": {"scenario_a": {"roads": left_frame["roads"]["changed_count"], "available_shelters": left_frame["available_shelter_count"], "evacuation_fraction": left_frame["assignment"]["evacuation_fraction"]}, "scenario_b": {"roads": right_frame["roads"]["changed_count"], "available_shelters": right_frame["available_shelter_count"], "evacuation_fraction": right_frame["assignment"]["evacuation_fraction"]}}, "provenance": "ADMIN_SCENARIO"}
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/training-route")
def training_route(payload: dict[str, Any]) -> dict[str, Any]:
    _ensure_presets()
    try:
        scenario = STORE.get(str(payload["scenario_id"]))
        time_minute = int(payload.get("time_minute", 0))
        graph, coords = _graph()
        facilities = _facilities()
        frame = resolve_frame(scenario, time_minute, _roads(graph, coords), facilities)
        origin = (float(payload["origin"]["latitude"]), float(payload["origin"]["longitude"]))
        destination = (float(payload["destination"]["latitude"]), float(payload["destination"]["longitude"]))
        return build_training_route(frame, graph, coords, origin, destination)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
