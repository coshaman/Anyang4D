from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from services.api.goal4a import STORE, _frame_payload
from services.ai_surrogate.explain import explain_features
from services.ai_surrogate.features import extract_features
from services.ai_surrogate.model import load_bundle, predict_bundle
from services.ai_surrogate.scenarios import generate_candidates

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models/scenario_triage/model.joblib"
router = APIRouter(prefix="/api/admin/goal5a", tags=["goal5a-ai-surrogate"])
_SCENARIOS: dict[str, Any] = {}


def _bundle() -> dict[str, Any]:
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=503, detail="AI_SURROGATE_MODEL_NOT_TRAINED")
    try:
        return load_bundle(MODEL_PATH)
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=f"AI_SURROGATE_UNAVAILABLE: {exc}") from exc


def _screen_one(bundle: dict[str, Any], scenario: Any) -> dict[str, Any]:
    features = extract_features(scenario)
    explanation = explain_features(features, bundle["metadata"])
    return predict_bundle(bundle, scenario.scenario_id, features, explanation).to_dict()


@router.post("/screen")
def screen(payload: dict[str, Any]) -> dict[str, Any]:
    bundle = _bundle()
    count = max(1, min(2000, int(payload.get("candidate_count", 100))))
    top_k = max(1, min(count, int(payload.get("top_k", 10))))
    seed = int(payload.get("seed", 5))
    started = time.perf_counter()
    candidates = generate_candidates(seed, count)
    for scenario in candidates:
        _SCENARIOS[scenario.scenario_id] = scenario
    predictions = [_screen_one(bundle, scenario) for scenario in candidates]
    predictions.sort(key=lambda item: item["ranking_score"] if item["ranking_score"] is not None else float("-inf"), reverse=True)
    shortlist = predictions[:top_k]
    exact_started = time.perf_counter()
    verified: list[dict[str, Any]] = []
    for item in shortlist:
        scenario = _SCENARIOS[item["scenario_id"]]
        exact = _frame_payload(scenario, scenario.frame_times()[-1])
        item["exact_result"] = exact["assignment"] | {"available_shelter_count": exact["available_shelter_count"], "time_minute": exact["time_minute"]}
        item["exact_verified"] = True
        item["authoritative_ordering_score"] = exact["assignment"]["unserved"] + 0.25 * exact["overloaded_shelter_count"] + 0.001 * float((exact["assignment"]["average_assigned_travel_distance_m"] or 0) * exact["assignment"]["assigned"])
        verified.append(item)
    verified.sort(key=lambda item: item["authoritative_ordering_score"], reverse=True)
    return {"workflow": ["candidate_generation", "AI_SURROGATE_SCREENING", "exact_top_k_verification"], "candidate_count": count, "top_k": top_k, "model_version": bundle["metadata"]["model_bundle_version"], "predictions": predictions, "verified_shortlist": verified, "exact_calls": len(verified), "elapsed_ms": round((time.perf_counter() - started) * 1000, 3), "exact_verification_ms": round((time.perf_counter() - exact_started) * 1000, 3), "provenance": "AI_SURROGATE", "citizen_guidance_authorized": False}


@router.post("/verify/{scenario_id}")
def verify(scenario_id: str) -> dict[str, Any]:
    bundle = _bundle()
    scenario = _SCENARIOS.get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="screening scenario not found; run screen first")
    prediction = _screen_one(bundle, scenario)
    exact = _frame_payload(scenario, scenario.frame_times()[-1])
    prediction["exact_result"] = exact
    prediction["exact_verified"] = True
    prediction["authoritative_result"] = exact
    return {"prediction": prediction, "exact_verified": True, "provenance": "AI_SURROGATE_PLUS_EXACT_REFERENCE", "citizen_guidance_authorized": False}


@router.get("/status")
def status() -> dict[str, Any]:
    if not MODEL_PATH.exists():
        return {"status": "AI_SURROGATE_MODEL_NOT_TRAINED", "screening_enabled": False, "exact_reference_available": True}
    bundle = _bundle()
    return {"status": "AI_SURROGATE_READY", "screening_enabled": True, "model_version": bundle["metadata"]["model_bundle_version"], "exact_reference_available": True, "exact_verification_required": True}
