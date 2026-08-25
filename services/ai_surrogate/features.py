from __future__ import annotations

import math
from functools import lru_cache
from typing import Any

from services.api.goal4a import _facilities, _graph, _roads
from services.simulator.data import load_population_demand
from services.simulator.engine import derive_evacuation_demand, resolve_frame

from . import FEATURE_SCHEMA_VERSION


@lru_cache(maxsize=1)
def _static() -> tuple[Any, dict[int, tuple[float, float]], list[dict[str, Any]], list[dict[str, Any]], dict[str, float], dict[str, float]]:
    graph, coords = _graph()
    roads = _roads(graph, coords)
    facilities = _facilities()
    demand = load_population_demand()
    edge_degree = {}
    for first, second in graph.edges():
        edge_degree[f"{first}-{second}"] = graph.degree(first) + graph.degree(second)
    edge_length = {str(road["edge_id"]): math.hypot(road["b"][0] - road["a"][0], road["b"][1] - road["a"][1]) for road in roads}
    return graph, coords, roads, facilities, edge_degree, edge_length


def extract_features(scenario) -> dict[str, float]:
    graph, coords, roads, facilities, edge_degree, edge_length = _static()
    time_minute = scenario.frame_times()[-1]
    frame = resolve_frame(scenario, time_minute, roads, facilities)
    demand = scenario.demand_units
    affected, meta = derive_evacuation_demand(frame, scenario, demand)
    features: dict[str, float] = {"feature_schema_version_hash": 1.0, "timestep_minutes": float(scenario.timestep_minutes), "evacuation_fraction": scenario.evacuation_fraction, "keyframe_count": float(len(scenario.hazard_keyframes)), "demand_node_count": float(len(demand)), "affected_demand_node_count": float(len(affected)), "total_population": float(meta["total_population"]), "affected_population": float(meta["affected_population"]), "evacuation_demand": float(meta["evacuation_demand"])}
    for disaster_type in ["FLOOD", "EARTHQUAKE", "FIRE", "CIVIL_DEFENSE", "GENERAL_EVACUATION"]:
        features[f"disaster_type_{disaster_type}"] = 1.0 if scenario.disaster_type == disaster_type else 0.0
    hazard = frame.hazard_geometry
    if hazard and hazard.get("kind") in {"polygon", "multipolygon"}:
        rings = hazard["coordinates"] if hazard["kind"] == "polygon" else [ring for polygon in hazard["coordinates"] for ring in polygon]
        points = [point for ring in rings for point in ring]
        features["hazard_min_lon"] = min(point[0] for point in points); features["hazard_max_lon"] = max(point[0] for point in points); features["hazard_min_lat"] = min(point[1] for point in points); features["hazard_max_lat"] = max(point[1] for point in points)
        features["hazard_area_proxy"] = (features["hazard_max_lon"] - features["hazard_min_lon"]) * (features["hazard_max_lat"] - features["hazard_min_lat"])
    else:
        features.update({"hazard_min_lon": 0.0, "hazard_max_lon": 0.0, "hazard_min_lat": 0.0, "hazard_max_lat": 0.0, "hazard_area_proxy": 0.0})
    closed = [edge_id for edge_id, state in frame.roads.items() if not state.available]
    features.update({"closed_edge_count": float(len(closed)), "closed_edge_length_m": float(sum(edge_length.get(edge_id, 0.0) for edge_id in closed)), "closed_edge_degree_sum": float(sum(edge_degree.get(edge_id, 0) for edge_id in closed)), "closed_high_degree_count": float(sum(edge_degree.get(edge_id, 0) >= 20 for edge_id in closed))})
    available = [facility for facility in facilities if frame.facilities[facility["id"]].available and facility.get("category") == "CIVIL_DEFENSE_SHELTER"]
    total_capacity = sum(frame.facilities[facility["id"]].effective_capacity for facility in available)
    closed_shelters = [facility for facility in facilities if facility.get("category") == "CIVIL_DEFENSE_SHELTER" and not frame.facilities[facility["id"]].available]
    features.update({"available_shelter_count": float(len(available)), "closed_shelter_count": float(len(closed_shelters)), "available_capacity": float(total_capacity), "capacity_to_demand_ratio": float(total_capacity / meta["evacuation_demand"]) if meta["evacuation_demand"] else 0.0, "lost_capacity": float(sum((facility.get("capacity") or 0) for facility in closed_shelters))})
    return {key: float(value) for key, value in sorted(features.items())}


def feature_names() -> list[str]:
    return list(extract_features(__import__("services.simulator.presets", fromlist=["build_presets"]).build_presets(_facilities(), load_population_demand())[0]).keys())


FEATURE_SCHEMA = FEATURE_SCHEMA_VERSION
