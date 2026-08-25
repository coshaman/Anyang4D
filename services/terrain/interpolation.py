from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .contracts import Bounds, ConstraintSet


@dataclass(frozen=True)
class IDWSurface:
    x: np.ndarray
    y: np.ndarray
    elevation: np.ndarray
    method: str
    grid_spacing_m: float


def _points(constraints: ConstraintSet) -> tuple[np.ndarray, np.ndarray]:
    points: dict[tuple[float, float], list[float]] = {}
    for item in [*constraints.contours, *constraints.spot_heights]:
        for point in item.geometry:
            points.setdefault(point, []).append(item.elevation_m)
    coords = sorted(points)
    xy = np.asarray(coords, dtype=float)
    z = np.asarray([sum(points[point]) / len(points[point]) for point in coords], dtype=float)
    return xy, z


def build_surface(constraints: ConstraintSet, bounds: Bounds, grid_spacing_m: float, *, method: str = "idw") -> IDWSurface:
    if method != "idw":
        raise ValueError("only deterministic idw is available")
    if grid_spacing_m <= 0:
        raise ValueError("grid_spacing_m must be positive")
    xy, z = _points(constraints)
    if len(xy) == 0:
        raise ValueError("at least one elevation constraint is required")
    xs = np.arange(bounds.west, bounds.east + grid_spacing_m * 0.5, grid_spacing_m, dtype=float)
    ys = np.arange(bounds.south, bounds.north + grid_spacing_m * 0.5, grid_spacing_m, dtype=float)
    gx, gy = np.meshgrid(xs, ys)
    values = np.empty_like(gx)
    for start in range(0, len(ys), 16):
        stop = min(start + 16, len(ys))
        dx = gx[start:stop, ..., None] - xy[:, 0]
        dy = gy[start:stop, ..., None] - xy[:, 1]
        distances = np.hypot(dx, dy)
        exact = distances == 0
        weights = 1.0 / np.maximum(distances, 1e-9) ** 2
        values[start:stop] = (weights * z).sum(axis=-1) / weights.sum(axis=-1)
        if exact.any():
            rows, cols = np.where(exact.any(axis=-1))
            for row, col in zip(rows, cols):
                values[start + row, col] = z[np.flatnonzero(exact[row, col])[0]]
    return IDWSurface(xs, ys, values, method, float(grid_spacing_m))
