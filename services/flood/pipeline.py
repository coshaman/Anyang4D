from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from .baseline import run_level_a_baseline
from .contracts import FloodScenarioInput, Provenance


def _array(frames: list[list[list[float | None]]]) -> np.ndarray:
    return np.asarray(frames, dtype=float)


def evaluate_predictions(predictions: list[list[list[float | None]]], truth: list[list[list[float | None]]]) -> dict[str, float]:
    pred = _array(predictions)
    actual = _array(truth)
    error = pred - actual
    abs_error = np.abs(error)
    wet_pred = pred >= 0.5
    wet_actual = actual >= 0.5
    union = np.logical_or(wet_pred, wet_actual).sum()
    intersection = np.logical_and(wet_pred, wet_actual).sum()
    delta = np.diff(pred, axis=0)
    return {
        "mae": float(abs_error.mean()),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "wet_dry_iou": float(intersection / union) if union else 1.0,
        "temporal_non_decrease_fraction": float(np.mean(delta >= -1e-8)) if delta.size else 1.0,
    }


def _synthetic_case(seed: int) -> tuple[FloodScenarioInput, list[list[list[float]]]]:
    rng = np.random.default_rng(seed)
    size = 16
    y, x = np.mgrid[0:size, 0:size]
    dem = 4.0 + (x / size) + (y / size)
    dem += 0.25 * np.sin(x / 2.0) * np.cos(y / 3.0)
    rainfall = [4.0, 10.0, 18.0, 28.0, 40.0, 55.0]
    scenario = FloodScenarioInput(
        scenario_id="synthetic-goal3b",
        dem=dem.round(5).tolist(),
        rainfall_mm_per_timestep=rainfall,
        timestep_minutes=5,
        duration_steps=len(rainfall),
        grid_resolution_m=1.0,
        crs="EPSG:5174",
        transform=[1, 0, 0, 0, -1, 0],
        rainfall_mode="SCENARIO",
        provenance=Provenance.SYNTHETIC,
    )
    valid = dem
    terrain = 1.0 - (valid - valid.min()) / (valid.max() - valid.min())
    truth = []
    for total in np.cumsum(rainfall):
        response = 1.0 - np.exp(-total / 24.0)
        spatial = 0.04 * np.sin((x + seed) / 3.0) * np.cos((y + seed) / 4.0)
        truth.append(np.clip(0.8 * terrain * response + spatial * response + rng.normal(0, 0.002, terrain.shape), 0, 1).tolist())
    return scenario, truth


def run_synthetic_evaluation(output_dir: Path, seed: int = 7) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    scenario, truth = _synthetic_case(seed)
    baseline = run_level_a_baseline(scenario)
    persistence = [np.zeros_like(np.asarray(truth[0])).tolist()] + [truth[index - 1] for index in range(1, len(truth))]
    baseline_metrics = evaluate_predictions(baseline.frames, truth)
    persistence_metrics = evaluate_predictions(persistence, truth)
    result = {
        "provenance": "SYNTHETIC",
        "field_kind": "RELATIVE_HAZARD",
        "seed": seed,
        "split": "single synthetic fixture; no Anyang validation",
        "baseline": baseline_metrics,
        "persistence": persistence_metrics,
        "backend": baseline.backend,
        "checkpoint": "deterministic baseline has no learned weights",
        "limitations": ["synthetic target is not water depth", "no drainage or calibration", "not an Anyang result"],
    }
    (output_dir / "config.json").write_text(json.dumps({"seed": seed, "scenario": scenario.model_dump(mode="json")}, indent=2), encoding="utf-8")
    (output_dir / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (output_dir / "deterministic-baseline-checkpoint.json").write_text(json.dumps({"backend": baseline.backend, "seed": seed}, indent=2), encoding="utf-8")
    np.savez_compressed(output_dir / "synthetic-target.npz", target=np.asarray(truth, dtype=np.float32), baseline=np.asarray(baseline.frames, dtype=np.float32))
    return result
