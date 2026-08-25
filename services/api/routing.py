from __future__ import annotations

import math
from typing import Any

import networkx as nx


WALKABLE = {
    "footway", "path", "pedestrian", "living_street", "residential", "service", "unclassified",
    "tertiary", "tertiary_link", "secondary", "secondary_link", "primary", "primary_link", "steps", "track",
}


def _graph(payload: dict[str, Any]) -> tuple[nx.Graph, dict[int, tuple[float, float]]]:
    nodes = {e["id"]: e for e in payload.get("elements", []) if e.get("type") == "node"}
    graph = nx.Graph()
    coords: dict[int, tuple[float, float]] = {}
    for node_id, node in nodes.items():
        coords[node_id] = (float(node["lat"]), float(node["lon"]))
    for way in (e for e in payload.get("elements", []) if e.get("type") == "way"):
        if way.get("tags", {}).get("highway") not in WALKABLE:
            continue
        sequence = [node for node in way.get("nodes", []) if node in coords]
        for a, b in zip(sequence, sequence[1:]):
            distance = _distance_m(coords[a], coords[b])
            graph.add_edge(a, b, distance_m=distance, walking_minutes=distance / 80.0)
    return graph, coords


def _distance_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    haversine = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6_371_000 * 2 * math.asin(math.sqrt(haversine))


def _nearest(coords: dict[int, tuple[float, float]], point: tuple[float, float]) -> int:
    return min(coords, key=lambda node: _distance_m(coords[node], point))


def build_route(payload: dict[str, Any], origin: tuple[float, float], destination: tuple[float, float]) -> dict[str, Any]:
    graph, coords = _graph(payload)
    if not coords:
        raise ValueError("no pedestrian path")
    start, end = _nearest(coords, origin), _nearest(coords, destination)
    try:
        path = nx.shortest_path(graph, start, end, weight="distance_m")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as exc:
        raise ValueError("no pedestrian path") from exc
    distance = sum(graph[a][b]["distance_m"] for a, b in zip(path, path[1:]))
    return {
        "geometry": [{"latitude": coords[node][0], "longitude": coords[node][1]} for node in path],
        "distance_m": round(distance, 1),
        "estimated_walking_minutes": max(1, round(distance / 80.0)),
        "destination": {"latitude": destination[0], "longitude": destination[1]},
        "provenance": "OFFICIAL",
        "hazard_exposure": None,
        "official_closure_reason": None,
        "simulated_hazard_exposure": None,
        "time_dependent_cost": None,
    }
