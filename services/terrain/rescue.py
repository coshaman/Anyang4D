from __future__ import annotations

from dataclasses import dataclass

import numpy as np
try:
    from shapely.geometry import LineString, Point
    from shapely.strtree import STRtree
except ImportError:  # pragma: no cover - exercised only in the minimal test runtime
    LineString = None
    Point = None
    STRtree = None

from .contracts import Bounds, ConstraintSet


@dataclass(frozen=True)
class ContourAwareSurface:
    x: np.ndarray
    y: np.ndarray
    elevation: np.ndarray
    method: str
    grid_spacing_m: float


def build_contour_aware_surface(constraints: ConstraintSet, bounds: Bounds, grid_spacing_m: float) -> ContourAwareSurface:
    if grid_spacing_m <= 0:
        raise ValueError("grid_spacing_m must be positive")
    grouped: dict[float, list[tuple[tuple[float, float], ...]]] = {}
    for item in constraints.contours:
        if len(item.geometry) >= 2:
            grouped.setdefault(float(item.elevation_m), []).append(item.geometry)
    levels = np.asarray(sorted(grouped), dtype=float)
    if len(levels) < 2:
        raise ValueError("contour-aware interpolation requires at least two contour elevations")
    xs = np.arange(bounds.west, bounds.east + grid_spacing_m * 0.5, grid_spacing_m, dtype=float)
    ys = np.arange(bounds.south, bounds.north + grid_spacing_m * 0.5, grid_spacing_m, dtype=float)
    gx, gy = np.meshgrid(xs, ys)
    flat = np.column_stack((gx.ravel(), gy.ravel()))
    distances = _contour_distances(flat, grouped, levels)
    pair_scores = distances[:, :-1] + distances[:, 1:]
    pair_index = np.argmin(pair_scores, axis=1)
    row = np.arange(len(flat))
    lower_distance = distances[row, pair_index]
    upper_distance = distances[row, pair_index + 1]
    lower_level = levels[pair_index]
    upper_level = levels[pair_index + 1]
    total_distance = np.maximum(lower_distance + upper_distance, 1e-9)
    elevation = (lower_level * upper_distance + upper_level * lower_distance) / total_distance
    return ContourAwareSurface(xs, ys, elevation.reshape(gx.shape), "contour_aware_distance", float(grid_spacing_m))


def predict_contour_aware(constraints: ConstraintSet, locations: list[tuple[float, float]]) -> np.ndarray:
    grouped: dict[float, list[tuple[tuple[float, float], ...]]] = {}
    for item in constraints.contours:
        if len(item.geometry) >= 2:
            grouped.setdefault(float(item.elevation_m), []).append(item.geometry)
    levels = np.asarray(sorted(grouped), dtype=float)
    if len(levels) < 2:
        raise ValueError("contour-aware interpolation requires at least two contour elevations")
    distances = _contour_distances(np.asarray(locations, dtype=float), grouped, levels)
    pair_index = np.argmin(distances[:, :-1] + distances[:, 1:], axis=1)
    row = np.arange(len(locations))
    lower_distance = distances[row, pair_index]
    upper_distance = distances[row, pair_index + 1]
    total_distance = np.maximum(lower_distance + upper_distance, 1e-9)
    return (levels[pair_index] * upper_distance + levels[pair_index + 1] * lower_distance) / total_distance


def _contour_distances(points: np.ndarray, grouped: dict[float, list[tuple[tuple[float, float], ...]]], levels: np.ndarray) -> np.ndarray:
    distances = np.empty((len(points), len(levels)), dtype=float)
    for index, level in enumerate(levels):
        if STRtree is not None:
            tree = STRtree([LineString(geometry) for geometry in grouped[float(level)]])
            for start in range(0, len(points), 4096):
                stop = min(start + 4096, len(points))
                shapely_points = [Point(float(x), float(y)) for x, y in points[start:stop]]
                _, nearest_distance = tree.query_nearest(shapely_points, all_matches=False, return_distance=True)
                distances[start:stop, index] = nearest_distance
        else:
            distances[:, index] = _fallback_distances(points, grouped[float(level)])
    return distances


def _fallback_distances(points: np.ndarray, lines: list[tuple[tuple[float, float], ...]]) -> np.ndarray:
    result = np.full(len(points), np.inf, dtype=float)
    for line in lines:
        for first, second in zip(line, line[1:]):
            dx, dy = second[0] - first[0], second[1] - first[1]
            denominator = dx * dx + dy * dy
            if denominator == 0:
                distance = np.hypot(points[:, 0] - first[0], points[:, 1] - first[1])
            else:
                t = np.clip(((points[:, 0] - first[0]) * dx + (points[:, 1] - first[1]) * dy) / denominator, 0, 1)
                distance = np.hypot(points[:, 0] - (first[0] + t * dx), points[:, 1] - (first[1] + t * dy))
            result = np.minimum(result, distance)
    return result
