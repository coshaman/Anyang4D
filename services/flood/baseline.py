"""Transparent Level-A terrain/rainfall baseline.

This is a relative scenario field. It is intentionally not a hydraulic depth
model: it has no sewer, inlet, building-blockage, roughness, or calibrated
loss terms.
"""

from __future__ import annotations

import numpy as np

from .contracts import FloodScenarioInput, FloodScenarioOutput


def _terrain_score(dem: np.ndarray) -> np.ndarray:
    valid = np.isfinite(dem)
    if not valid.any():
        raise ValueError("DEM contains no valid cells")
    values = dem[valid]
    low = float(values.min())
    high = float(values.max())
    global_low = np.ones_like(dem, dtype=float) if high == low else 1.0 - (dem - low) / (high - low)
    padded = np.pad(dem, 1, mode="edge")
    neighborhood_max = np.full_like(dem, -np.inf, dtype=float)
    for row in range(3):
        for col in range(3):
            neighborhood_max = np.maximum(neighborhood_max, padded[row : row + dem.shape[0], col : col + dem.shape[1]])
    local_depression = np.clip(neighborhood_max - dem, 0.0, None)
    local_scale = float(np.nanmax(local_depression[valid]))
    depression_score = np.zeros_like(dem, dtype=float) if local_scale == 0 else local_depression / local_scale
    score = 0.7 * global_low + 0.3 * depression_score
    score[~valid] = np.nan
    return np.clip(score, 0.0, 1.0)


def run_level_a_baseline(scenario: FloodScenarioInput) -> FloodScenarioOutput:
    dem = np.asarray(scenario.dem, dtype=float)
    terrain = _terrain_score(dem)
    cumulative = np.cumsum(np.asarray(scenario.rainfall_mm_per_timestep, dtype=float))
    peak = max(float(cumulative.max()), 1.0)
    frames: list[list[list[float | None]]] = []
    class_frames: list[list[list[int | None]]] = []
    for rainfall_total in cumulative:
        hazard = terrain * (float(rainfall_total) / peak)
        frame: list[list[float | None]] = []
        class_frame: list[list[int | None]] = []
        for row in range(hazard.shape[0]):
            frame.append([None if not np.isfinite(value) else round(float(value), 6) for value in hazard[row]])
            class_frame.append([None if not np.isfinite(value) else int(1 + (value >= 0.33) + (value >= 0.66)) for value in hazard[row]])
        frames.append(frame)
        class_frames.append(class_frame)
    return FloodScenarioOutput(
        scenario_id=scenario.scenario_id,
        times=[index * scenario.timestep_minutes for index in range(scenario.duration_steps)],
        field_kind="RELATIVE_HAZARD",
        frames=frames,
        crs=scenario.crs,
        transform=scenario.transform,
        grid_resolution_m=scenario.grid_resolution_m,
        provenance=scenario.provenance,
        fidelity_level="A",
        backend="safetwin-deterministic-level-a-v1",
        assumptions=[
            "lower relative elevation and local depression increase hazard",
            "rainfall accumulates without modeled recession",
            "no drainage, sewer, inlet, building blockage, roughness, or calibrated loss model",
        ],
        limitations=["relative scenario hazard only; not predicted water depth"],
    )


def classify_level_a(output: FloodScenarioOutput) -> list[list[list[int | None]]]:
    if output.field_kind != "RELATIVE_HAZARD":
        raise ValueError("classification expects RELATIVE_HAZARD output")
    return [
        [[None if value is None else int(1 + (value >= 0.33) + (value >= 0.66)) for value in row] for row in frame]
        for frame in output.frames
    ]
