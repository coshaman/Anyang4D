from __future__ import annotations

import math

import numpy as np


def elevation_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float | int]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    mask = np.isfinite(actual) & np.isfinite(predicted)
    if not mask.any():
        return {"count": 0, "mae_m": math.inf, "rmse_m": math.inf, "median_abs_error_m": math.inf, "p95_abs_error_m": math.inf, "max_abs_error_m": math.inf}
    error = np.abs(actual[mask] - predicted[mask])
    signed = actual[mask] - predicted[mask]
    return {
        "count": int(mask.sum()),
        "mae_m": float(np.mean(error)),
        "rmse_m": float(np.sqrt(np.mean(signed ** 2))),
        "median_abs_error_m": float(np.median(error)),
        "p95_abs_error_m": float(np.percentile(error, 95)),
        "max_abs_error_m": float(np.max(error)),
    }


def terrain_diagnostics(elevation: np.ndarray, grid_spacing_m: float) -> dict[str, float | int]:
    values = np.asarray(elevation, dtype=float)
    valid = np.isfinite(values)
    if grid_spacing_m <= 0:
        raise ValueError("grid_spacing_m must be positive")
    dy, dx = np.gradient(np.where(valid, values, np.nan), grid_spacing_m, grid_spacing_m)
    slope = np.hypot(dx, dy)
    finite_slope = slope[np.isfinite(slope)]
    finite_values = values[valid]
    flow_direction_counts, flow_accumulation = _d8_diagnostics(values)
    return {
        "cell_count": int(values.size),
        "valid_cell_count": int(valid.sum()),
        "invalid_cell_count": int((~valid).sum()),
        "coverage_fraction": float(valid.mean()),
        "elevation_min_m": float(np.min(finite_values)) if finite_values.size else math.nan,
        "elevation_max_m": float(np.max(finite_values)) if finite_values.size else math.nan,
        "slope_p99": float(np.percentile(finite_slope, 99)) if finite_slope.size else math.inf,
        "negative_slope_cell_count": int(np.sum(finite_slope < 0)),
        "sink_cell_count": int(_sink_count(values)),
        "flow_direction_counts": flow_direction_counts,
        "flow_accumulation_max": float(np.max(flow_accumulation[valid])) if valid.any() else math.nan,
        "flow_accumulation_finite": bool(np.isfinite(flow_accumulation[valid]).all()),
    }


def _sink_count(values: np.ndarray) -> int:
    count = 0
    for row in range(1, values.shape[0] - 1):
        for col in range(1, values.shape[1] - 1):
            value = values[row, col]
            if np.isfinite(value) and np.all(value <= values[row - 1:row + 2, col - 1:col + 2]):
                count += 1
    return count


def _d8_diagnostics(values: np.ndarray) -> tuple[dict[str, int], np.ndarray]:
    directions = {(dr, dc): name for (dr, dc), name in zip(
        [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)],
        ["NW", "N", "NE", "W", "FLAT", "E", "SW", "S", "SE"],
    )}
    counts = {name: 0 for name in directions.values()}
    valid = np.isfinite(values)
    accumulation = np.where(valid, 1.0, np.nan)
    downstream: dict[tuple[int, int], tuple[int, int] | None] = {}
    for row, col in zip(*np.where(valid)):
        best = float(values[row, col])
        target = None
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < values.shape[0] and 0 <= nc < values.shape[1] and np.isfinite(values[nr, nc]) and values[nr, nc] < best:
                    best = float(values[nr, nc])
                    target = (nr, nc)
        downstream[(row, col)] = target
        counts[directions[(target[0] - row, target[1] - col)] if target else "FLAT"] += 1
    for row, col in sorted(downstream, key=lambda cell: values[cell], reverse=True):
        target = downstream[(row, col)]
        if target is not None:
            accumulation[target] += accumulation[(row, col)]
    return counts, accumulation


def classify_quality(report: dict[str, object]) -> str:
    spot = report.get("spot", {})
    def number(value: object, default: float) -> float:
        return default if value is None else float(value)
    contour_p95 = number(report.get("contour_p95_m"), math.inf)
    seam_p95 = number(report.get("seam_p95_m"), math.inf)
    seam_median = number(report.get("seam_median_m"), math.inf)
    road_p95 = number(report.get("road_p95_m"), math.inf)
    coverage = number(report.get("coverage"), 0)
    slope_p99 = number(report.get("slope_p99"), math.inf)
    spot_mae = number(spot.get("mae_m"), math.inf)
    spot_p95 = number(spot.get("p95_abs_error_m"), math.inf)
    if spot_mae <= 2 and spot_p95 <= 5 and contour_p95 <= 2.5 and seam_p95 <= 2 and seam_median <= 1 and road_p95 <= 50 and coverage >= 1 and slope_p99 <= 1.5:
        return "TERRAIN_A"
    if spot_mae <= 3 and spot_p95 <= 10 and contour_p95 <= 5 and seam_p95 <= 5 and road_p95 <= 100 and coverage >= 1 and slope_p99 <= 2:
        return "TERRAIN_B"
    return "TERRAIN_C"
