from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Iterable

from services.api.goal4a import _facilities, _frame_payload, _graph, _roads
from services.simulator.engine import eligible_facilities, resolve_frame

from . import REFERENCE_ENGINE_VERSION
from .features import extract_features

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = ROOT / "data/derived/ai_scenario_surrogate"


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_hashes() -> dict[str, str]:
    return {name: _sha(ROOT / relative) for name, relative in {"manifest": "data/manifests/data_manifest.json", "facilities": "data/processed/anyang_facilities.json", "population": "data/processed/anyang_population.json"}.items()}


def _label(scenario, feature_row: dict[str, float]) -> dict[str, Any]:
    started = time.perf_counter()
    frame_time = scenario.frame_times()[-1]
    payload = _frame_payload(scenario, frame_time)
    graph, coords = _graph()
    frame = resolve_frame(scenario, frame_time, _roads(graph, coords), _facilities())
    eligible = eligible_facilities(scenario, _facilities())
    available_capacity = sum(frame.facilities[item["id"]].effective_capacity for item in eligible if frame.facilities[item["id"]].available)
    assignment = payload["assignment"]
    assigned = float(assignment["assigned"])
    assignment_cost = float(assignment["average_assigned_travel_distance_m"] or 0) * assigned
    return {
        "scenario_id": scenario.scenario_id,
        "scenario": scenario.to_dict(),
        "scenario_family": next((item for item in scenario.assumptions if item.startswith("family=")), "family=UNKNOWN").split("=", 1)[-1],
        "features": feature_row,
        "reference_outputs": {
            "assigned": assigned,
            "unserved": float(assignment["unserved"]),
            "assignment_cost": assignment_cost,
            "available_capacity_deficit": float(max(0, assignment["evacuation_demand"] - available_capacity)),
            "overloaded_shelter_count": float(payload["overloaded_shelter_count"]),
            "ranking_score": float(assignment["unserved"] + 0.25 * payload["overloaded_shelter_count"] + 0.001 * assignment_cost),
        },
        "exact_state_signatures": {"computation_state_signature": payload["computation_state_signature"], "roads": payload["roads"], "facilities": payload["facilities"], "demand": {"affected_ids": assignment["affected_demand_ids"], "evacuation_demand": assignment["evacuation_demand"]}},
        "label_provenance": "REFERENCE_SIMULATION_LABEL",
        "reference_engine_version": REFERENCE_ENGINE_VERSION,
        "label_runtime_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def generate_labels(candidates: Iterable[Any], output_dir: Path = DEFAULT_DIR, resume: bool = True) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows_path = output_dir / "labels.jsonl"
    existing: dict[str, dict[str, Any]] = {}
    if resume and rows_path.exists():
        for line in rows_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line); existing[row["scenario_id"]] = row
    candidates = list(candidates)
    with rows_path.open("a", encoding="utf-8") as handle:
        for scenario in candidates:
            if scenario.scenario_id in existing:
                continue
            features = extract_features(scenario)
            row = _label(scenario, features)
            row["source_hashes"] = source_hashes()
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            existing[scenario.scenario_id] = row
    manifest = {"schema_version": "goal5a-dataset-v1", "record_count": len(existing), "scenario_ids": sorted(existing), "source_hashes": source_hashes(), "reference_engine_version": REFERENCE_ENGINE_VERSION, "label_provenance": "REFERENCE_SIMULATION_LABEL", "generator": "services.ai_surrogate.scenarios.generate_candidates", "resume": resume}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def load_rows(path: Path = DEFAULT_DIR / "labels.jsonl") -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
