from __future__ import annotations

from typing import Any
import json
from pathlib import Path

import networkx as nx


WALKABLE_HIGHWAYS = {
    "footway",
    "path",
    "pedestrian",
    "living_street",
    "residential",
    "service",
    "unclassified",
    "tertiary",
    "tertiary_link",
    "secondary",
    "secondary_link",
    "primary",
    "primary_link",
    "steps",
    "track",
}


def build_walk_graph(payload: dict[str, Any]) -> dict[str, Any]:
    nodes = {element["id"]: element for element in payload.get("elements", []) if element.get("type") == "node"}
    graph = nx.Graph()
    highway_tags: dict[str, int] = {}
    for way in (element for element in payload.get("elements", []) if element.get("type") == "way"):
        highway = way.get("tags", {}).get("highway")
        if highway not in WALKABLE_HIGHWAYS:
            continue
        highway_tags[highway] = highway_tags.get(highway, 0) + 1
        way_nodes = [node_id for node_id in way.get("nodes", []) if node_id in nodes]
        graph.add_nodes_from(way_nodes)
        graph.add_edges_from(zip(way_nodes, way_nodes[1:]))
    components = list(nx.connected_components(graph)) if graph else []
    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "component_count": len(components),
        "largest_component_node_count": max((len(component) for component in components), default=0),
        "largest_component_fraction": (max((len(component) for component in components), default=0) / graph.number_of_nodes()) if graph else 0.0,
        "walkable_highway_way_counts": highway_tags,
    }


def audit_osm_file(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = build_walk_graph(payload)
    result.update({"path": path.as_posix(), "element_count": len(payload.get("elements", [])), "columns": []})
    return result
