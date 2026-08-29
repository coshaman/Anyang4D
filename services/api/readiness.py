from __future__ import annotations

import json
import re
import networkx as nx
from functools import lru_cache
from pathlib import Path
from typing import Any

from services.ai_surrogate.model import load_bundle
from services.simulator.data import load_population_demand, load_simulation_facilities, load_simulation_graph


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/manifests/data_manifest.json"
MODEL_PATH = ROOT / "models/scenario_triage/model.joblib"


def _safe_error(exc: Exception) -> str:
    message = str(exc).splitlines()[0][:160] or type(exc).__name__
    return re.sub(r"[A-Za-z]:[\\/][^ ]+", "artifact", message)


def _source_versions() -> dict[str, Any]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = {}
    for item in payload.get("datasets", []):
        sources[item["id"]] = {
            "status": item.get("status"),
            "retrieved_at": item.get("retrieved_at") or item.get("retrieval_timestamp"),
            "temporal_coverage": item.get("temporal_coverage"),
            "sha256": item.get("sha256"),
        }
    return sources


@lru_cache(maxsize=1)
def readiness_payload() -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    try:
        facilities = load_simulation_facilities()
        counts = {}
        for item in facilities:
            counts[item["category"]] = counts.get(item["category"], 0) + 1
        checks["facility_data_loaded"] = {"ready": counts.get("CIVIL_DEFENSE_SHELTER") == 231 and counts.get("EMERGENCY_WATER") == 71, "counts": counts}
    except Exception as exc:  # pragma: no cover - readiness must report, not crash
        checks["facility_data_loaded"] = {"ready": False, "error": _safe_error(exc)}

    try:
        units = load_population_demand()
        total = sum(int(unit["population"]) for unit in units)
        checks["population_loaded"] = {"ready": len(units) == 31 and total == 562143, "units": len(units), "total_population": total, "source_period": "2026-07-31"}
    except Exception as exc:  # pragma: no cover
        checks["population_loaded"] = {"ready": False, "error": _safe_error(exc)}

    try:
        graph, _ = load_simulation_graph()
        checks["osm_graph_loaded"] = {"ready": graph.number_of_nodes() > 0 and graph.number_of_edges() > 0, "nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(), "source": "osm-anyang-pedestrian-demo"}
    except Exception as exc:  # pragma: no cover
        checks["osm_graph_loaded"] = {"ready": False, "error": _safe_error(exc)}

    checks["scenario_engine_ready"] = {"ready": (ROOT / "data/scenarios/goal4a").exists()}
    try:
        broad_path = ROOT / "data/raw/openstreetmap/anyang_pedestrian_broad/overpass.json"
        broad_payload = json.loads(broad_path.read_text(encoding="utf-8"))
        broad_graph, _ = __import__("services.api.routing", fromlist=["_graph"])._graph(broad_payload)
        checks["osm_broad_routing_graph_loaded"] = {"ready": broad_graph.number_of_nodes() > 0 and broad_graph.number_of_edges() > 0, "nodes": broad_graph.number_of_nodes(), "edges": broad_graph.number_of_edges(), "source": "osm-anyang-pedestrian-broad"}
    except Exception as exc:  # pragma: no cover
        checks["osm_broad_routing_graph_loaded"] = {"ready": False, "error": _safe_error(exc)}
    try:
        probe = nx.DiGraph()
        probe.add_node("source", demand=-1)
        probe.add_node("sink", demand=1)
        probe.add_edge("source", "sink", capacity=1, weight=1)
        nx.min_cost_flow(probe)
        checks["exact_solver_ready"] = {"ready": True, "solver": "NetworkX deterministic min-cost flow"}
    except Exception as exc:  # pragma: no cover
        checks["exact_solver_ready"] = {"ready": False, "solver": "NetworkX deterministic min-cost flow", "error": _safe_error(exc)}
    if MODEL_PATH.exists():
        try:
            bundle = load_bundle(MODEL_PATH)
            metadata = bundle["metadata"]
            checks["ai_model_loaded"] = {"ready": True, "model_version": metadata["model_bundle_version"], "feature_schema_version": metadata["feature_schema_version"], "model_name": metadata["model_name"]}
        except Exception as exc:  # pragma: no cover
            checks["ai_model_loaded"] = {"ready": False, "error": _safe_error(exc)}
    else:
        checks["ai_model_loaded"] = {"ready": False, "error": "model bundle missing"}

    mandatory = ["facility_data_loaded", "population_loaded", "osm_graph_loaded", "osm_broad_routing_graph_loaded", "scenario_engine_ready", "exact_solver_ready", "ai_model_loaded"]
    source_versions = _source_versions()
    closed_research_sources = [source_id for source_id, item in source_versions.items() if item.get("status") == "CLOSED_RESEARCH_BRANCH"]
    return {
        "status": "READY" if all(checks[name]["ready"] for name in mandatory) else "NOT_READY",
        "backend_ready": True,
        "mandatory_checks": checks,
        "ai_decision": "AI_SURROGATE_B / ADMIN_AI_SCENARIO_SCREENING=DEMO_ONLY",
        "exact_reference_engine": "goal4b-exact-reference-v1",
        "source_versions": source_versions,
        "missing_optional_sources": [source_id for source_id, item in source_versions.items() if item.get("status") not in {"DOWNLOADED", "CLOSED_RESEARCH_BRANCH"}],
        "closed_research_sources": closed_research_sources,
        "frozen_boundary": {"final_terrain_class": "TERRAIN_C", "high_res_terrain_acquisition": "CLOSED", "terrain_dependency_for_release": False, "street_level_flood_terrain_path": "DROP", "citizen_hazard_routing_from_terrain": "DROP"},
    }
