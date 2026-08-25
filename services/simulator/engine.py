from __future__ import annotations

from dataclasses import dataclass, replace
import math
import time
from typing import Any

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import networkx as nx

_ROAD_INDEX_CACHE: dict[int, tuple[Any, tuple[str, ...]]] = {}
_COORDS_CACHE: dict[int, dict[int, tuple[float, float]]] = {}
_SNAP_CACHE: dict[tuple[int, float, float], int | None] = {}
_ACTIVE_GRAPH_CACHE: dict[tuple[int, tuple[str, ...]], Any] = {}


def clear_engine_caches() -> None:
    _ROAD_INDEX_CACHE.clear()
    _COORDS_CACHE.clear()
    _SNAP_CACHE.clear()
    _ACTIVE_GRAPH_CACHE.clear()

from .contracts import DemandUnit, Scenario


@dataclass(frozen=True)
class FacilityState:
    facility_id: str
    available: bool
    effective_capacity: int
    reason: str | None
    provenance: str


@dataclass(frozen=True)
class RoadState:
    edge_id: str
    available: bool
    reasons: tuple[str, ...]
    provenance: tuple[str, ...]


@dataclass(frozen=True)
class ResourceState:
    resource_id: str
    available: bool
    reason: str | None
    provenance: str


@dataclass
class WorldFrame:
    scenario_id: str
    time_minute: int
    hazard_geometry: dict[str, Any] | None
    hazard_label: str | None
    roads: dict[str, RoadState]
    facilities: dict[str, FacilityState]
    resources: dict[str, ResourceState]
    provenance: str


def resolve_frame(scenario: Scenario, time_minute: int, roads: list[dict[str, Any]], facilities: list[dict[str, Any]], resources: list[dict[str, Any]] | None = None) -> WorldFrame:
    if time_minute not in scenario.frame_times():
        raise ValueError("time_minute must be one of the scenario frame times")
    keyframes = [item for item in scenario.hazard_keyframes if item.time_minute <= time_minute]
    keyframe = keyframes[-1] if keyframes else None
    hazard = keyframe.geometry if keyframe else None
    hazard_candidates = _hazard_candidate_edge_ids(hazard, roads) if hazard else None
    road_states: dict[str, RoadState] = {}
    for edge in roads:
        edge_id = str(edge["edge_id"])
        reasons: list[str] = []
        provenance: list[str] = []
        for event in scenario.road_closure_events:
            if event.start_minute <= time_minute < event.end_minute and edge_id in event.edge_ids:
                reasons.append(event.reason)
                provenance.append(event.provenance)
        if hazard and (hazard_candidates is None or edge_id in hazard_candidates) and _hazard_intersects_segment(hazard, edge["a"], edge["b"]):
            reasons.append("시나리오 hazard geometry와 교차하여 통행 제한으로 설정된 도로")
            provenance.append("ADMIN_SCENARIO")
        road_states[edge_id] = RoadState(edge_id, not reasons, tuple(reasons), tuple(provenance))
    facility_states: dict[str, FacilityState] = {}
    for facility in facilities:
        facility_id = str(facility["id"])
        available = True
        reason = None
        for event in scenario.facility_events:
            if event.facility_id == facility_id and event.start_minute <= time_minute < event.end_minute:
                available, reason = event.available, event.reason
        if hazard and facility.get("latitude") is not None and _hazard_contains_point(hazard, (float(facility["longitude"]), float(facility["latitude"]))):
            available = False
            reason = "시나리오 hazard geometry와 교차하여 시설을 사용 불가로 설정"
        capacity = int(facility.get("capacity") or 0)
        for override in scenario.capacity_overrides:
            if override.facility_id == facility_id and override.start_minute <= time_minute < override.end_minute:
                capacity = override.capacity
                reason = override.reason if available else reason
        facility_states[facility_id] = FacilityState(facility_id, available and capacity > 0, max(0, capacity), reason, "ADMIN_SCENARIO" if reason else str(facility.get("provenance", "STALE_OR_UNKNOWN")))
    resource_states: dict[str, ResourceState] = {}
    for resource in resources or []:
        resource_id = str(resource["id"])
        available = True
        reason = None
        for event in scenario.resource_events:
            if event.resource_id == resource_id and event.start_minute <= time_minute < event.end_minute:
                available, reason = event.available, event.reason
        resource_states[resource_id] = ResourceState(resource_id, available, reason, "ADMIN_SCENARIO" if reason else str(resource.get("provenance", "OFFICIAL")))
    return WorldFrame(scenario.scenario_id, time_minute, hazard, keyframe.label if keyframe else None, road_states, facility_states, resource_states, scenario.provenance)


def eligible_facilities(scenario: Scenario, facilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if scenario.eligible_facility_ids:
        allowed = set(scenario.eligible_facility_ids)
        return [facility for facility in facilities if facility["id"] in allowed]
    category = {"CIVIL_DEFENSE": "CIVIL_DEFENSE_SHELTER", "FLOOD": "CIVIL_DEFENSE_SHELTER", "FIRE": "CIVIL_DEFENSE_SHELTER", "GENERAL_EVACUATION": "CIVIL_DEFENSE_SHELTER"}.get(scenario.disaster_type)
    if category is None:
        return []
    return [facility for facility in facilities if facility.get("category") == category]


def _rounded_participation(population: int, fraction: float) -> int:
    return int(math.floor(population * fraction + 0.5))


def derive_evacuation_demand(frame: WorldFrame, scenario: Scenario, demand_units: list[DemandUnit]) -> tuple[list[DemandUnit], dict[str, Any]]:
    """Select affected residents and apply an explicit participation assumption."""
    total_population = sum(unit.population for unit in demand_units)
    selected_ids = set(scenario.affected_demand_ids)
    if selected_ids:
        affected = [unit for unit in demand_units if unit.demand_id in selected_ids]
        rule = "EXPLICIT_DEMAND_SELECTION"
    elif frame.hazard_geometry is not None:
        affected = [unit for unit in demand_units if _hazard_contains_point(frame.hazard_geometry, (unit.longitude, unit.latitude))]
        rule = "ACTIVE_HAZARD_CONTAINMENT"
    elif scenario.disaster_type == "CIVIL_DEFENSE":
        affected = list(demand_units)
        rule = "CIVIL_DEFENSE_CITYWIDE_INTENT"
    else:
        affected = []
        rule = "NO_ACTIVE_AFFECTED_AREA"
    affected_population = sum(unit.population for unit in affected)
    evacuation_demand = _rounded_participation(affected_population, scenario.evacuation_fraction)
    scaled: list[DemandUnit] = []
    if affected_population:
        raw = [unit.population * scenario.evacuation_fraction for unit in affected]
        values = [int(math.floor(value)) for value in raw]
        remainder = evacuation_demand - sum(values)
        order = sorted(range(len(affected)), key=lambda index: (-(raw[index] - values[index]), affected[index].demand_id))
        for index in order[:max(0, remainder)]:
            values[index] += 1
        scaled = [replace(unit, population=population) for unit, population in zip(affected, values) if population > 0]
    return scaled, {"total_population": total_population, "affected_population": affected_population, "evacuation_demand": sum(unit.population for unit in scaled), "evacuation_fraction": scenario.evacuation_fraction, "affected_demand_rule": rule, "affected_demand_ids": [unit.demand_id for unit in affected], "provenance": "ADMIN_SCENARIO_ASSUMPTION"}


def solve_assignment(frame: WorldFrame, scenario: Scenario, demand_units: list[DemandUnit], facilities: list[dict[str, Any]], graph: nx.Graph, coords: dict[int, tuple[float, float]], timing: dict[str, float] | None = None) -> dict[str, Any]:
    import networkx as nx
    started = time.perf_counter()
    closed_edges = tuple(sorted(edge_id for edge_id, state in frame.roads.items() if not state.available))
    graph_key = (id(graph), closed_edges)
    active_graph = _ACTIVE_GRAPH_CACHE.get(graph_key)
    if active_graph is None:
        active_graph = graph.copy()
        for first, second, data in list(active_graph.edges(data=True)):
            edge_id = str(data.get("edge_id", f"{first}-{second}"))
            if edge_id in closed_edges:
                active_graph.remove_edge(first, second)
        _ACTIVE_GRAPH_CACHE[graph_key] = active_graph
    if timing is not None:
        timing["road_graph_mutation_ms"] = (time.perf_counter() - started) * 1000
    snap_started = time.perf_counter()
    eligible = [facility for facility in eligible_facilities(scenario, facilities) if frame.facilities.get(facility["id"], FacilityState(facility["id"], False, 0, "not in frame", "STALE_OR_UNKNOWN")).available]
    total_demand = sum(unit.population for unit in demand_units)
    demand_nodes = {unit.demand_id: _nearest_node(coords, (unit.latitude, unit.longitude)) for unit in demand_units}
    facility_nodes = {facility["id"]: _nearest_node(coords, (facility.get("latitude"), facility.get("longitude"))) for facility in eligible}
    if timing is not None:
        timing["demand_facility_snapping_ms"] = (time.perf_counter() - snap_started) * 1000
    shortest_started = time.perf_counter()
    distance_maps = {}
    for node in set(value for value in demand_nodes.values() if value is not None):
        try:
            distance_maps[node] = nx.single_source_dijkstra_path_length(active_graph, node, weight="distance_m")
        except nx.NodeNotFound:
            distance_maps[node] = {}
    if timing is not None:
        timing["shortest_paths_od_ms"] = (time.perf_counter() - shortest_started) * 1000
    flow_started = time.perf_counter()
    flow = nx.DiGraph()
    reachable_total = 0
    source, sink = "__source__", "__sink__"
    flow.add_node(source, demand=-total_demand)
    flow.add_node(sink, demand=total_demand)
    for unit in demand_units:
        demand_node = f"demand:{unit.demand_id}"
        flow.add_edge(source, demand_node, capacity=unit.population, weight=0)
        nearest = demand_nodes[unit.demand_id]
        reachable_for_unit = False
        for facility in eligible:
            facility_node = f"facility:{facility['id']}"
            target = facility_nodes[facility["id"]]
            if nearest is None or target is None:
                continue
            distance = distance_maps.get(nearest, {}).get(target)
            if distance is None:
                continue
            reachable_for_unit = True
            flow.add_edge(demand_node, facility_node, capacity=unit.population, weight=int(round(distance)))
        if reachable_for_unit:
            reachable_total += unit.population
        flow.add_edge(demand_node, f"unserved:{unit.demand_id}", capacity=unit.population, weight=10_000_000)
        flow.add_edge(f"unserved:{unit.demand_id}", sink, capacity=unit.population, weight=0)
    for facility in eligible:
        state = frame.facilities[facility["id"]]
        flow.add_edge(f"facility:{facility['id']}", sink, capacity=state.effective_capacity, weight=0)
    try:
        result = nx.min_cost_flow(flow)
    except nx.NetworkXUnfeasible:
        result = {node: {} for node in flow.nodes}
    if timing is not None:
        timing["min_cost_flow_ms"] = (time.perf_counter() - flow_started) * 1000
    assignments = []
    facility_load: dict[str, int] = {facility["id"]: 0 for facility in eligible}
    facility_by_id = {facility["id"]: facility for facility in eligible}
    demand_by_id = {unit.demand_id: unit for unit in demand_units}
    bottleneck_counts: dict[str, int] = {}
    assigned_distance_total = 0.0
    unserved = 0
    extraction_started = time.perf_counter()
    for unit in demand_units:
        node = result.get(f"demand:{unit.demand_id}", {})
        for facility in eligible:
            amount = int(node.get(f"facility:{facility['id']}", 0))
            if amount:
                facility_load[facility["id"]] += amount
                start = demand_nodes[unit.demand_id]
                end = facility_nodes[facility["id"]]
                path = nx.shortest_path(active_graph, start, end, weight="distance_m") if start is not None and end is not None else []
                distance = sum(active_graph[first][second].get("distance_m", 0) for first, second in zip(path, path[1:]))
                assigned_distance_total += amount * distance
                for first, second in zip(path, path[1:]):
                    edge_id = str(active_graph[first][second].get("edge_id", f"{first}-{second}"))
                    bottleneck_counts[edge_id] = bottleneck_counts.get(edge_id, 0) + amount
                assignments.append({"demand_id": unit.demand_id, "facility_id": facility["id"], "assigned": amount, "travel_distance_m": round(distance, 1), "reason": "capacity-constrained min-cost assignment"})
        unserved += int(node.get(f"unserved:{unit.demand_id}", unit.population))
    assigned = total_demand - unserved
    if timing is not None:
        timing["bottleneck_extraction_ms"] = (time.perf_counter() - extraction_started) * 1000
        timing["assignment_total_ms"] = (time.perf_counter() - started) * 1000
    return {"assigned": assigned, "unserved": unserved, "reachable_population": reachable_total, "total_demand": total_demand, "assignments": assignments, "facility_load": facility_load, "overloaded_facilities": [key for key, value in facility_load.items() if value > frame.facilities[key].effective_capacity], "average_assigned_travel_distance_m": round(assigned_distance_total / assigned, 1) if assigned else None, "bottleneck_edges": [{"edge_id": edge_id, "assigned_flow": flow} for edge_id, flow in sorted(bottleneck_counts.items(), key=lambda item: (-item[1], item[0]))[:20]], "provenance": scenario.provenance}


def build_training_route(frame: WorldFrame, graph, coords: dict[int, tuple[float, float]], origin: tuple[float, float], destination: tuple[float, float]) -> dict[str, Any]:
    import networkx as nx
    active_graph = graph.copy()
    for first, second, data in list(active_graph.edges(data=True)):
        edge_id = str(data.get("edge_id", f"{first}-{second}"))
        if edge_id in frame.roads and not frame.roads[edge_id].available:
            active_graph.remove_edge(first, second)
    start, end = _nearest_node(coords, origin), _nearest_node(coords, destination)
    if start is None or end is None:
        return {"status": "UNREACHABLE_IN_TRAINING_SCENARIO", "provenance": "ADMIN_SCENARIO", "reason": "origin or destination is outside the training graph"}
    try:
        path = nx.shortest_path(active_graph, start, end, weight="distance_m")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return {"status": "UNREACHABLE_IN_TRAINING_SCENARIO", "provenance": "ADMIN_SCENARIO", "reason": "scenario closure disconnects the selected training route"}
    distance = sum(active_graph[first][second].get("distance_m", 0) for first, second in zip(path, path[1:]))
    return {"status": "TRAINING_SCENARIO_ROUTE", "provenance": "ADMIN_SCENARIO", "warning": "훈련 시나리오 경로 · 실제 재난 시 공식 통제정보를 우선 확인하세요.", "geometry": [{"latitude": coords[node][0], "longitude": coords[node][1]} for node in path], "distance_m": round(distance, 1), "estimated_walking_minutes": max(1, round(distance / 80))}


def _nearest_node(coords: dict[int, tuple[float, float]], point: tuple[float | None, float | None]) -> int | None:
    if point[0] is None or point[1] is None or not coords:
        return None
    identity = id(coords)
    _COORDS_CACHE[identity] = coords
    key = (identity, round(float(point[0]), 7), round(float(point[1]), 7))
    if key not in _SNAP_CACHE:
        _SNAP_CACHE[key] = min(coords, key=lambda node: _distance_m(coords[node], (float(point[0]), float(point[1]))))
    return _SNAP_CACHE[key]


def _hazard_candidate_edge_ids(geometry: dict[str, Any], roads: list[dict[str, Any]]) -> set[str] | None:
    """Use a static STRtree candidate query, then retain custom exact checks."""
    try:
        from shapely.geometry import LineString, MultiPolygon, Point, Polygon
        from shapely.strtree import STRtree
        identity = id(roads)
        cached = _ROAD_INDEX_CACHE.get(identity)
        if cached is None:
            geometries = tuple(LineString([edge["a"], edge["b"]]) for edge in roads)
            cached = (STRtree(geometries), tuple(str(edge["edge_id"]) for edge in roads))
            _ROAD_INDEX_CACHE[identity] = cached
        tree, edge_ids = cached
        kind = geometry.get("kind")
        if kind == "polygon":
            hazard = Polygon(geometry["coordinates"][0])
        elif kind == "multipolygon":
            hazard = MultiPolygon([Polygon(item[0]) for item in geometry["coordinates"]])
        elif kind == "point_radius":
            lon, lat = geometry["center"]
            hazard = Point(lon, lat).buffer(float(geometry["radius_m"]) / 111000)
        elif kind == "corridor":
            hazard = LineString(geometry["coordinates"]).buffer(float(geometry["buffer_m"]) / 111000)
        else:
            return None
        result = tree.query(hazard)
        return {edge_ids[int(index)] for index in result}
    except Exception:
        return None


def _distance_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6_371_000 * 2 * math.asin(math.sqrt(value))


def _hazard_contains_point(geometry: dict[str, Any], point: tuple[float, float]) -> bool:
    kind = geometry.get("kind")
    if kind == "polygon":
        return _point_in_ring(point, geometry["coordinates"][0])
    if kind == "multipolygon":
        return any(_point_in_ring(point, polygon[0]) for polygon in geometry["coordinates"])
    if kind == "point_radius":
        center = geometry["center"]
        return _distance_m((point[1], point[0]), (center[1], center[0])) <= float(geometry["radius_m"])
    if kind == "corridor":
        return _distance_to_polyline_m(point, geometry["coordinates"]) <= float(geometry["buffer_m"])
    return False


def _hazard_intersects_segment(geometry: dict[str, Any], a: tuple[float, float], b: tuple[float, float]) -> bool:
    if _hazard_contains_point(geometry, a) or _hazard_contains_point(geometry, b) or _hazard_contains_point(geometry, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)):
        return True
    if geometry.get("kind") == "polygon":
        ring = geometry["coordinates"][0]
        return any(_segments_intersect(a, b, c, d) for c, d in zip(ring, ring[1:]))
    return False


def _point_in_ring(point: tuple[float, float], ring: list[list[float]]) -> bool:
    x, y = point
    inside = False
    for index in range(len(ring)):
        x1, y1 = ring[index - 1]
        x2, y2 = ring[index]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1:
            inside = not inside
    return inside


def _segments_intersect(a, b, c, d) -> bool:
    def orient(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return orient(a, b, c) * orient(a, b, d) <= 0 and orient(c, d, a) * orient(c, d, b) <= 0


def _distance_to_polyline_m(point, line) -> float:
    return min(_planar_distance(point, a, b) for a, b in zip(line, line[1:])) if len(line) > 1 else math.inf


def _planar_distance(point, a, b) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1e-12)))
    return _distance_m((point[1], point[0]), (a[1] + t * dy, a[0] + t * dx))
