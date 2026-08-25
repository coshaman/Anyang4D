from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

TARGETS = ["assigned", "unserved", "assignment_cost", "available_capacity_deficit", "overloaded_shelter_count"]


def _group(row: dict[str, Any]) -> str:
    features = row["features"]
    sector = f"{int(float(features.get('hazard_min_lon', 0)) * 100)}-{int(float(features.get('hazard_min_lat', 0)) * 100)}"
    return f"{row.get('scenario_family', 'UNKNOWN')}|{sector}"


def build_grouped_split(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for row in rows:
        groups.setdefault(_group(row), []).append(row["scenario_id"])
    ordered = sorted(groups)
    ood = [group for group in ordered if group.split("|", 1)[0] in {"MULTI_AREA_CORRELATED", "CONNECTIVITY_BREAK"}]
    remaining = [group for group in ordered if group not in ood]
    test_groups = [group for index, group in enumerate(remaining) if index % 5 == 0]
    val_groups = [group for index, group in enumerate(remaining) if index % 5 == 1]
    train_groups = [group for group in remaining if group not in test_groups + val_groups]
    return {"train": [item for group in train_groups for item in groups[group]], "validation": [item for group in val_groups for item in groups[group]], "test": [item for group in test_groups for item in groups[group]], "ood": [item for group in ood for item in groups[group]], "groups": ordered}


def _arrays(rows: list[dict[str, Any]], ids: list[str], feature_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    by_id = {row["scenario_id"]: row for row in rows}
    selected = [by_id[item] for item in ids]
    x = np.asarray([[row["features"][name] for name in feature_names] for row in selected], dtype=float)
    y = np.asarray([[row["reference_outputs"][target] for target in TARGETS] for row in selected], dtype=float)
    return x, y


def _ranking_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    actual_score = actual[:, TARGETS.index("unserved")] + 0.25 * actual[:, TARGETS.index("overloaded_shelter_count")] + 0.001 * actual[:, TARGETS.index("assignment_cost")]
    predicted_score = predicted[:, TARGETS.index("unserved")] + 0.25 * predicted[:, TARGETS.index("overloaded_shelter_count")] + 0.001 * predicted[:, TARGETS.index("assignment_cost")]
    if len(actual_score) < 2:
        return {"spearman": 0.0, "recall_at_20": 0.0, "precision_at_20": 0.0, "ndcg_at_20": 0.0}
    if np.allclose(actual_score, actual_score[0]) or np.allclose(predicted_score, predicted_score[0]):
        correlation = 0.0
    else:
        raw_correlation = spearmanr(actual_score, predicted_score).statistic
        correlation = float(raw_correlation) if raw_correlation is not None and np.isfinite(raw_correlation) else 0.0
    k = min(20, len(actual_score))
    actual_top = set(np.argsort(-actual_score)[:k]); predicted_top = list(np.argsort(-predicted_score)[:k])
    hits = sum(index in actual_top for index in predicted_top)
    gains = {index: actual_score[index] for index in range(len(actual_score))}
    dcg = sum(max(0.0, gains[index]) / math.log2(position + 2) for position, index in enumerate(predicted_top))
    ideal = list(np.argsort(-actual_score)[:k])
    idcg = sum(max(0.0, gains[index]) / math.log2(position + 2) for position, index in enumerate(ideal)) or 1.0
    return {"spearman": round(correlation, 6), "recall_at_20": round(hits / max(1, len(actual_top)), 6), "precision_at_20": round(hits / k, 6), "ndcg_at_20": round(dcg / idcg, 6)}


def metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for index, target in enumerate(TARGETS):
        errors = np.abs(actual[:, index] - predicted[:, index])
        denominator = max(float(np.sum((actual[:, index] - np.mean(actual[:, index])) ** 2)), 1e-9)
        r2 = 1 - float(np.sum((actual[:, index] - predicted[:, index]) ** 2)) / denominator
        result[target] = {"mae": round(float(np.mean(errors)), 6), "rmse": round(float(np.sqrt(np.mean((actual[:, index] - predicted[:, index]) ** 2))), 6), "median_absolute_error": round(float(np.median(errors)), 6), "p90_absolute_error": round(float(np.percentile(errors, 90)), 6), "p95_absolute_error": round(float(np.percentile(errors, 95)), 6), "r2": round(r2, 6)}
    result["ranking"] = _ranking_metrics(actual, predicted)
    return result


def candidate_models() -> dict[str, Any]:
    return {"ridge": Pipeline([("scale", StandardScaler()), ("model", MultiOutputRegressor(Ridge(alpha=10.0))) ]), "hist_gradient_boosting": MultiOutputRegressor(HistGradientBoostingRegressor(max_iter=120, learning_rate=0.06, max_leaf_nodes=15, l2_regularization=1.0, random_state=17))}


def evaluate_models(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) < 8:
        raise ValueError("at least 8 labeled scenarios are required for evaluation")
    split = build_grouped_split(rows)
    feature_names = sorted(rows[0]["features"])
    train_x, train_y = _arrays(rows, split["train"], feature_names)
    validation_x, validation_y = _arrays(rows, split["validation"], feature_names) if split["validation"] else (train_x, train_y)
    test_x, test_y = _arrays(rows, split["test"], feature_names) if split["test"] else (train_x, train_y)
    ood_x, ood_y = _arrays(rows, split["ood"], feature_names) if split["ood"] else (test_x, test_y)
    results: dict[str, Any] = {"split": split, "feature_names": feature_names, "targets": TARGETS, "baselines": {}, "models": {}, "ood": {}}
    median_prediction = np.tile(np.median(train_y, axis=0), (len(validation_y), 1))
    results["baselines"]["median"] = metrics(validation_y, median_prediction)
    trained: dict[str, Any] = {}
    for name, model in candidate_models().items():
        model.fit(train_x, train_y)
        trained[name] = model
        results["models"][name] = {"validation": metrics(validation_y, model.predict(validation_x)), "test": metrics(test_y, model.predict(test_x)), "ood": metrics(ood_y, model.predict(ood_x))}
    results["selected_model"] = max(trained, key=lambda name: results["models"][name]["validation"]["ranking"]["ndcg_at_20"] - 0.000001 * results["models"][name]["validation"]["unserved"]["mae"])
    results["selected_model_validation"] = results["models"][results["selected_model"]]["validation"]
    ablations = {"without_official_population": {name for name in feature_names if name in {"total_population", "affected_population", "evacuation_demand"}}, "without_official_capacity": {name for name in feature_names if "capacity" in name or "shelter" in name or name == "lost_capacity"}, "without_graph_disruption": {name for name in feature_names if "closed_edge" in name}}
    results["ablations"] = {}
    for ablation_name, removed in ablations.items():
        masked_names = [name for name in feature_names if name not in removed]
        train_x_mask, _ = _arrays(rows, split["train"], masked_names)
        validation_x_mask, _ = _arrays(rows, split["validation"], masked_names) if split["validation"] else (train_x_mask, train_y)
        model = candidate_models()[results["selected_model"]]
        model.fit(train_x_mask, train_y)
        results["ablations"][ablation_name] = {"removed_features": sorted(removed), "validation": metrics(validation_y, model.predict(validation_x_mask))}
    return {"results": results, "models": trained}


def write_evaluation(artifact: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact["results"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
