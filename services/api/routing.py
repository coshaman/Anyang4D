from __future__ import annotations

import math
from typing import Any

import networkx as nx


WALKABLE = {
    "footway", "path", "pedestrian", "living_street", "residential", "service", "unclassified",
    "tertiary", "tertiary_link", "secondary", "secondary_link", "primary", "primary_link", "steps", "track",
}

_GRAPH_CACHE: dict[int, tuple[nx.Graph, dict[int, tuple[float, float]]]] = {}


def _graph(payload: dict[str, Any]) -> tuple[nx.Graph, dict[int, tuple[float, float]]]:
    cached = _GRAPH_CACHE.get(id(payload))
    if cached is not None:
        return cached
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
    result = (graph, coords)
    _GRAPH_CACHE[id(payload)] = result
    if len(_GRAPH_CACHE) > 2:
        _GRAPH_CACHE.pop(next(iter(_GRAPH_CACHE)))
    return result


def _distance_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    haversine = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6_371_000 * 2 * math.asin(math.sqrt(haversine))


def _nearest(coords: dict[int, tuple[float, float]], point: tuple[float, float]) -> int:
    return min(coords, key=lambda node: _distance_m(coords[node], point))


def build_routes(payload: dict[str, Any], origin: tuple[float, float], destination: tuple[float, float], limit: int = 2) -> list[dict[str, Any]]:
    graph, coords = _graph(payload)
    if not coords:
        raise ValueError("no pedestrian path")
    start, end = _nearest(coords, origin), _nearest(coords, destination)
    try:
        primary = nx.shortest_path(graph, start, end, weight="distance_m")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as exc:
        raise ValueError("no pedestrian path") from exc
    paths = [primary]
    if limit > 1 and len(primary) > 2:
        # A full k-shortest-simple-paths search can expand exponentially on
        # the city graph. Probe a bounded set of primary-path edges instead;
        # this returns a real distinct alternative when the graph permits it.
        probe_edges = list(zip(primary, primary[1:]))[:24]
        for blocked_a, blocked_b in probe_edges:
            edge_data = dict(graph.get_edge_data(blocked_a, blocked_b) or {})
            graph.remove_edge(blocked_a, blocked_b)
            try:
                alternative = nx.shortest_path(graph, start, end, weight="distance_m")
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                alternative = None
            finally:
                graph.add_edge(blocked_a, blocked_b, **edge_data)
            if alternative and alternative != primary:
                paths.append(alternative)
                break
    routes = []
    for index, path in enumerate(paths, start=1):
        distance = sum(graph[a][b]["distance_m"] for a, b in zip(path, path[1:]))
        routes.append({
            "candidate_index": index,
            "geometry": [{"latitude": coords[node][0], "longitude": coords[node][1]} for node in path],
            "distance_m": round(distance, 1),
            "estimated_walking_minutes": max(1, round(distance / 80.0)),
            "destination": {"latitude": destination[0], "longitude": destination[1]},
            "provenance": "OFFICIAL",
            "hazard_exposure": None,
            "official_closure_reason": None,
            "simulated_hazard_exposure": None,
            "time_dependent_cost": None,
        })
    return routes


def build_route(payload: dict[str, Any], origin: tuple[float, float], destination: tuple[float, float]) -> dict[str, Any]:
    return build_routes(payload, origin, destination, limit=1)[0]
