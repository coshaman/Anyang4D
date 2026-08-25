from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from services.api.routing import _graph

ROOT = Path(__file__).resolve().parents[2]


def load_simulation_facilities() -> list[dict[str, Any]]:
    payload = json.loads((ROOT / "data/processed/anyang_facilities.json").read_text(encoding="utf-8"))
    records = payload.get("records", [])
    return [record for record in records if record.get("category") in {"CIVIL_DEFENSE_SHELTER", "EMERGENCY_WATER"}]


def load_population_demand() -> list[dict[str, Any]]:
    payload = json.loads((ROOT / "data/processed/anyang_population.json").read_text(encoding="utf-8"))
    return list(payload.get("units", []))


def load_local_resource_context() -> dict[str, list[dict[str, Any]]]:
    payload = json.loads((ROOT / "data/processed/anyang_local_resources.json").read_text(encoding="utf-8"))
    return {
        "water": list(payload.get("water", {}).get("normalized_items", [])),
        "flood_response_inventory": list(payload.get("flood_response_inventory", {}).get("normalized_items", [])),
    }


def load_simulation_graph():
    # Goal 4A uses the bounded demo snapshot for interactive what-if frames;
    # the broad snapshot remains the citizen-route source.
    payload = json.loads((ROOT / "data/raw/openstreetmap/anyang_pedestrian_demo/overpass.json").read_text(encoding="utf-8"))
    graph, coords = _graph(payload)
    for first, second, data in graph.edges(data=True):
        data["edge_id"] = f"{first}-{second}"
    return graph, coords
