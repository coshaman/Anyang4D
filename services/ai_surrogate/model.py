from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from . import FEATURE_SCHEMA_VERSION, MODEL_BUNDLE_VERSION
from .contracts import SurrogatePrediction, validate_feature_schema
from .evaluate import TARGETS, evaluate_models


def train_bundle(rows: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    evaluated = evaluate_models(rows)
    model_name = evaluated["results"]["selected_model"]
    model = evaluated["models"][model_name]
    feature_names = evaluated["results"]["feature_names"]
    train_ids = set(evaluated["results"]["split"]["train"])
    train_rows = [row for row in rows if row["scenario_id"] in train_ids]
    matrix = np.asarray([[row["features"][name] for name in feature_names] for row in train_rows], dtype=float)
    lower = matrix.min(axis=0).tolist(); upper = matrix.max(axis=0).tolist(); mean = matrix.mean(axis=0).tolist(); std = np.maximum(matrix.std(axis=0), 1e-9).tolist()
    metadata = {"model_bundle_version": MODEL_BUNDLE_VERSION, "feature_schema_version": FEATURE_SCHEMA_VERSION, "model_name": model_name, "feature_names": feature_names, "targets": TARGETS, "support_lower": lower, "support_upper": upper, "support_mean": mean, "support_std": std, "evaluation": evaluated["results"], "training_ids": sorted(train_ids), "validation_ids": evaluated["results"]["split"]["validation"], "test_ids": evaluated["results"]["split"]["test"], "ood_ids": evaluated["results"]["split"]["ood"], "provenance": "AI_SURROGATE", "exact_verification_required": True, "license": "BSD-3-Clause (scikit-learn), BSD-3-Clause (joblib)"}
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "metadata": metadata}, output_dir / "model.joblib")
    (output_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata


def load_bundle(path: Path) -> dict[str, Any]:
    bundle = joblib.load(path)
    if bundle.get("metadata", {}).get("model_bundle_version") != MODEL_BUNDLE_VERSION:
        raise ValueError("model bundle version mismatch")
    if bundle.get("metadata", {}).get("feature_schema_version") != FEATURE_SCHEMA_VERSION:
        raise ValueError("feature schema version mismatch")
    return bundle


def support_status(features: dict[str, float], metadata: dict[str, Any]) -> str:
    names = metadata["feature_names"]
    validate_feature_schema(features, names)
    values = np.asarray([features[name] for name in names], dtype=float)
    lower = np.asarray(metadata["support_lower"], dtype=float); upper = np.asarray(metadata["support_upper"], dtype=float)
    if np.any(values < lower - 1e-9) or np.any(values > upper + 1e-9):
        return "AI_ESTIMATE_UNSUPPORTED"
    return "AI_ESTIMATE_SUPPORTED"


def predict_bundle(bundle: dict[str, Any], scenario_id: str, features: dict[str, float], explanation: list[dict[str, Any]] | None = None) -> SurrogatePrediction:
    metadata = bundle["metadata"]
    status = support_status(features, metadata)
    if status != "AI_ESTIMATE_SUPPORTED":
        return SurrogatePrediction(scenario_id=scenario_id, support_status=status, explanation=explanation or [])
    vector = np.asarray([[features[name] for name in metadata["feature_names"]]], dtype=float)
    values = bundle["model"].predict(vector)[0]
    output = dict(zip(metadata["targets"], [float(value) for value in values]))
    score = output["unserved"] + 0.25 * output["overloaded_shelter_count"] + 0.001 * output["assignment_cost"]
    return SurrogatePrediction(scenario_id=scenario_id, estimated_assigned=output["assigned"], estimated_unserved=output["unserved"], estimated_assignment_cost=output["assignment_cost"], estimated_capacity_deficit=output["available_capacity_deficit"], estimated_overloaded_shelter_count=output["overloaded_shelter_count"], ranking_score=score, support_status=status, explanation=explanation or [])
