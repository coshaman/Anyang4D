from datetime import datetime, timezone

import networkx as nx

from services.simulator.contracts import DemandUnit, Scenario
from services.simulator.engine import build_training_route, resolve_frame, solve_assignment


def _scenario(closure=False, facility_closed=False) -> Scenario:
    data = {
        "scenario_id": "assignment-fixture", "title": "훈련/가정 시나리오", "disaster_type": "GENERAL_EVACUATION",
        "start_time": "2026-08-22T00:00:00+00:00", "end_time": "2026-08-22T00:20:00+00:00", "timestep_minutes": 10,
        "provenance": "ADMIN_SCENARIO", "description": "fixture", "assumptions": [],
        "hazard_keyframes": [], "road_closure_events": [], "facility_events": [], "capacity_overrides": [],
        "demand_units": [{"demand_id": "d1", "label": "수요", "latitude": 0, "longitude": 0, "population": 5, "provenance": "ADMIN_SCENARIO"}],
    }
    if closure:
        data["road_closure_events"] = [{"start_minute": 10, "end_minute": 20, "edge_ids": ["1-2"], "reason": "시나리오 통행 제한", "provenance": "ADMIN_SCENARIO"}]
    if facility_closed:
        data["facility_events"] = [{"start_minute": 10, "end_minute": 20, "facility_id": "s1", "available": False, "reason": "시설 폐쇄", "provenance": "ADMIN_SCENARIO"}]
    return Scenario.from_dict(data)


def _graph():
    graph = nx.Graph()
    graph.add_edge(1, 2, edge_id="1-2", distance_m=10)
    graph.add_edge(2, 3, edge_id="2-3", distance_m=10)
    return graph, {1: (0, 0), 2: (0, 0.001), 3: (0, 0.002)}


def _facility():
    return [{"id": "s1", "category": "CIVIL_DEFENSE_SHELTER", "latitude": 0, "longitude": 0.002, "capacity": 3, "provenance": "OFFICIAL"}]


def test_assignment_conserves_demand_and_respects_capacity():
    scenario = _scenario()
    frame = resolve_frame(scenario, 0, [{"edge_id": "1-2", "a": (0, 0), "b": (0.001, 0)}, {"edge_id": "2-3", "a": (0.001, 0), "b": (0.002, 0)}], _facility())
    result = solve_assignment(frame, scenario, scenario.demand_units, _facility(), *_graph())
    assert result["assigned"] + result["unserved"] == result["total_demand"] == 5
    assert result["facility_load"]["s1"] == 3
    assert result["unserved"] == 2


def test_timeline_road_and_facility_changes_change_assignment():
    scenario = _scenario(closure=True, facility_closed=True)
    roads = [{"edge_id": "1-2", "a": (0, 0), "b": (0.001, 0)}, {"edge_id": "2-3", "a": (0.001, 0), "b": (0.002, 0)}]
    facilities = _facility()
    graph, coords = _graph()
    open_result = solve_assignment(resolve_frame(scenario, 0, roads, facilities), scenario, scenario.demand_units, facilities, graph, coords)
    changed_result = solve_assignment(resolve_frame(scenario, 10, roads, facilities), scenario, scenario.demand_units, facilities, graph, coords)
    assert resolve_frame(scenario, 0, roads, facilities).roads["1-2"].available is True
    assert resolve_frame(scenario, 10, roads, facilities).roads["1-2"].available is False
    assert changed_result["assigned"] < open_result["assigned"]
    assert changed_result["facility_load"].get("s1", 0) == 0


def test_training_route_responds_to_scenario_closure():
    scenario = _scenario(closure=True)
    graph, coords = _graph()
    roads = [{"edge_id": "1-2", "a": (0, 0), "b": (0.001, 0)}, {"edge_id": "2-3", "a": (0.001, 0), "b": (0.002, 0)}]
    open_route = build_training_route(resolve_frame(scenario, 0, roads, _facility()), graph, coords, (0, 0), (0, 0.002))
    closed_route = build_training_route(resolve_frame(scenario, 10, roads, _facility()), graph, coords, (0, 0), (0, 0.002))
    assert open_route["status"] == "TRAINING_SCENARIO_ROUTE"
    assert closed_route["status"] == "UNREACHABLE_IN_TRAINING_SCENARIO"


def test_three_frame_4d_difference_road_then_shelter_outage():
    data = _scenario(closure=True).to_dict()
    data["facility_events"] = [{"start_minute": 20, "end_minute": 30, "facility_id": "s1", "available": False, "reason": "시설 폐쇄", "provenance": "ADMIN_SCENARIO"}]
    scenario = Scenario.from_dict(data)
    roads = [{"edge_id": "1-2", "a": (0, 0), "b": (0.001, 0)}, {"edge_id": "2-3", "a": (0.001, 0), "b": (0.002, 0)}, {"edge_id": "1-4", "a": (0, 0), "b": (0.001, 0.001)}, {"edge_id": "4-3", "a": (0.001, 0.001), "b": (0.002, 0)}]
    facilities = _facility()
    graph = nx.Graph()
    graph.add_edge(1, 2, edge_id="1-2", distance_m=10)
    graph.add_edge(2, 3, edge_id="2-3", distance_m=10)
    graph.add_edge(1, 4, edge_id="1-4", distance_m=15)
    graph.add_edge(4, 3, edge_id="4-3", distance_m=15)
    coords = {1: (0, 0), 2: (0, 0.001), 3: (0, 0.002), 4: (0.001, 0.001)}
    results = [solve_assignment(resolve_frame(scenario, minute, roads, facilities), scenario, scenario.demand_units, facilities, graph, coords) for minute in (0, 10, 20)]
    assert results[0]["assigned"] == results[1]["assigned"] == 3
    assert results[1]["average_assigned_travel_distance_m"] > results[0]["average_assigned_travel_distance_m"]
    assert results[2]["assigned"] == 0
    assert resolve_frame(scenario, 10, roads, facilities).roads["1-2"].available is False
    assert resolve_frame(scenario, 20, roads, facilities).facilities["s1"].available is False
