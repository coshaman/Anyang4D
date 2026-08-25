from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any

from services.api.goal4a import _facilities, _graph
from services.simulator.contracts import Scenario
from services.simulator.data import load_population_demand


def _polygon(cx: float, cy: float, width: float, height: float) -> dict[str, Any]:
    ring = [[cx - width, cy - height], [cx + width, cy - height], [cx + width, cy + height], [cx - width, cy + height], [cx - width, cy - height]]
    return {"kind": "polygon", "coordinates": [ring]}


def _base(scenario_id: str, family: str, disaster_type: str, demand: list[dict[str, Any]]) -> dict[str, Any]:
    start = datetime(2026, 8, 22, tzinfo=timezone.utc)
    return {
        "scenario_id": scenario_id, "title": f"Goal5A {family} {scenario_id}", "disaster_type": disaster_type,
        "start_time": start.isoformat(), "end_time": (start + timedelta(minutes=30)).isoformat(), "timestep_minutes": 10,
        "provenance": "SIMULATED_ADMIN_SCENARIO", "description": "AI surrogate training/administrative what-if only",
        "assumptions": ["SIMULATED_ADMIN_SCENARIO", "AI labels are REFERENCE_SIMULATION_LABEL", "terrain flood path disabled"],
        "hazard_keyframes": [], "road_closure_events": [], "facility_events": [], "capacity_overrides": [], "resource_events": [],
        "demand_units": demand, "affected_demand_ids": [], "evacuation_fraction": 1.0,
        "affected_demand_rule": "HAZARD_CONTAINMENT_OR_EXPLICIT_SELECTION", "audit_log": [], "_family": family,
    }


def generate_candidates(seed: int = 5, count: int = 160) -> list[Scenario]:
    if count <= 0:
        return []
    rng = random.Random(seed)
    demand = load_population_demand()
    facilities = [item for item in _facilities() if item.get("category") == "CIVIL_DEFENSE_SHELTER" and item.get("latitude") is not None and item.get("longitude") is not None]
    graph, coords = _graph()
    edges = [data.get("edge_id", f"{first}-{second}") for first, second, data in graph.edges(data=True)]
    families = ["LIGHT", "MODERATE_MULTI_ROAD", "MAJOR_FACILITY_OUTAGE", "CAPACITY_SHORTAGE", "CONNECTIVITY_BREAK", "HIGH_PARTICIPATION", "LOCALIZED_HAZARD", "MULTI_AREA_CORRELATED"]
    scenarios: list[Scenario] = []
    for index in range(count):
        family = families[index % len(families)]
        item = _base(f"goal5a-{seed:03d}-{index:04d}", family, "GENERAL_EVACUATION", demand)
        item["assumptions"].append(f"family={family}")
        cx = 126.90 + rng.random() * 0.09
        cy = 37.36 + rng.random() * 0.08
        width = 0.006 + rng.random() * (0.025 if family not in {"LOCALIZED_HAZARD", "LIGHT"} else 0.012)
        height = 0.006 + rng.random() * (0.018 if family not in {"LOCALIZED_HAZARD", "LIGHT"} else 0.010)
        hazard = _polygon(cx, cy, width, height)
        item["hazard_keyframes"] = [{"time": 0, "label": f"{family} simulated administrative area", "geometry": hazard}]
        item["evacuation_fraction"] = {"HIGH_PARTICIPATION": 1.0, "CAPACITY_SHORTAGE": 0.75}.get(family, rng.choice([0.25, 0.5, 0.75, 1.0]))
        closure_count = {"LIGHT": 1, "MODERATE_MULTI_ROAD": 3, "CONNECTIVITY_BREAK": 6, "MULTI_AREA_CORRELATED": 4}.get(family, 0)
        if closure_count:
            picked = rng.sample(edges, min(closure_count, len(edges)))
            item["road_closure_events"] = [{"start_minute": 0, "end_minute": 30, "edge_ids": picked, "reason": "SIMULATED_ADMIN_SCENARIO road closure", "provenance": "SIMULATED_ADMIN_SCENARIO"}]
        if family in {"MAJOR_FACILITY_OUTAGE", "CAPACITY_SHORTAGE", "MULTI_AREA_CORRELATED"} and facilities:
            outage_count = 1 if family != "MULTI_AREA_CORRELATED" else min(3, len(facilities))
            selected = rng.sample(facilities, outage_count)
            if family == "CAPACITY_SHORTAGE":
                item["capacity_overrides"] = [{"start_minute": 0, "end_minute": 30, "facility_id": f["id"], "capacity": max(1, int((f.get("capacity") or 1) * 0.25)), "reason": "SIMULATED_ADMIN_SCENARIO capacity reduction", "provenance": "SIMULATED_ADMIN_SCENARIO"} for f in selected]
            else:
                item["facility_events"] = [{"start_minute": 0, "end_minute": 30, "facility_id": f["id"], "available": False, "reason": "SIMULATED_ADMIN_SCENARIO shelter outage", "provenance": "SIMULATED_ADMIN_SCENARIO"} for f in selected]
        if family == "MULTI_AREA_CORRELATED":
            item["hazard_keyframes"] = [{"time": 0, "label": "multi-area simulated administrative areas", "geometry": {"kind": "multipolygon", "coordinates": [hazard["coordinates"], _polygon(cx + 0.025, cy + 0.012, width * 0.7, height * 0.7)["coordinates"]]}}]
        if family == "CONNECTIVITY_BREAK" and edges:
            item["road_closure_events"][0]["edge_ids"] = edges[:min(closure_count, len(edges))]
        scenarios.append(Scenario.from_dict(item))
    return scenarios
