from __future__ import annotations

from collections import Counter, defaultdict
import math

from .contracts import ConstraintSet, ElevationConstraint

try:
    from shapely.geometry import LineString
    from shapely.strtree import STRtree
except ImportError:  # pragma: no cover - fallback is covered by fixture tests
    LineString = None
    STRtree = None


def _canonical_geometry(item: ElevationConstraint) -> tuple[tuple[float, float], ...]:
    forward = tuple((round(x, 3), round(y, 3)) for x, y in item.geometry)
    reverse = tuple(reversed(forward))
    return min(forward, reverse)


def _orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_cross(a, b, c, d) -> bool:
    if max(a[0], b[0]) < min(c[0], d[0]) or max(c[0], d[0]) < min(a[0], b[0]) or max(a[1], b[1]) < min(c[1], d[1]) or max(c[1], d[1]) < min(a[1], b[1]):
        return False
    eps = 1e-9
    return (_orientation(a, b, c) * _orientation(a, b, d) < -eps or abs(_orientation(a, b, c)) <= eps and abs(_orientation(a, b, d)) > eps) and (_orientation(c, d, a) * _orientation(c, d, b) < -eps or abs(_orientation(c, d, a)) <= eps and abs(_orientation(c, d, b)) > eps)


def _crossing(a: ElevationConstraint, b: ElevationConstraint) -> bool:
    for first, second in zip(a.geometry, a.geometry[1:]):
        for third, fourth in zip(b.geometry, b.geometry[1:]):
            if _segments_cross(first, second, third, fourth):
                return True
    return False


def audit_contour_topology(sets: list[ConstraintSet], boundary_tolerance_m: float = 5.0) -> dict[str, object]:
    contours = [item for result in sets for item in result.contours]
    elevations = sorted({round(item.elevation_m, 6) for item in contours})
    intervals = Counter(round(second - first, 6) for first, second in zip(elevations, elevations[1:]) if second > first)
    geometry_groups: dict[tuple[tuple[float, float], ...], list[ElevationConstraint]] = defaultdict(list)
    for item in contours:
        geometry_groups[(_canonical_geometry(item), round(item.elevation_m, 3))].append(item)
    duplicate_count = sum(len(items) - 1 for items in geometry_groups.values() if len(items) > 1)
    closed = [item for item in contours if len(item.geometry) > 2 and item.geometry[0] == item.geometry[-1]]
    dangling = sum(0 if item in closed else 2 for item in contours)
    crossing_pairs = _crossing_pair_count(contours)
    boundary_continuations = 0
    for left_index, left in enumerate(sets):
        for right in sets[left_index + 1:]:
            for first in left.contours:
                for second in right.contours:
                    if round(first.elevation_m, 3) != round(second.elevation_m, 3):
                        continue
                    if any(math.dist(a, b) <= boundary_tolerance_m for a in (first.geometry[0], first.geometry[-1]) for b in (second.geometry[0], second.geometry[-1])):
                        boundary_continuations += 1
    return {
        "contour_count": len(contours),
        "unique_elevations_m": elevations,
        "interval_distribution_m": {str(key): value for key, value in sorted(intervals.items())},
        "constant_elevation_polyline_count": len(contours),
        "nonconstant_elevation_polyline_count": 0,
        "crossing_pair_count": crossing_pairs,
        "dangling_endpoint_count": dangling,
        "closed_contour_count": len(closed),
        "duplicate_geometry_count": duplicate_count,
        "tile_boundary_continuation_pair_count": boundary_continuations,
        "vertical_ordering_anomaly_count": sum(1 for first, second in zip(elevations, elevations[1:]) if second <= first),
        "boundary_tolerance_m": boundary_tolerance_m,
    }


def _crossing_pair_count(contours: list[ElevationConstraint]) -> int:
    if STRtree is not None and contours:
        lines = [LineString(item.geometry) for item in contours]
        pairs = STRtree(lines).query(lines, predicate="crosses")
        return sum(1 for left, right in zip(pairs[0], pairs[1]) if left < right and contours[left].source_sheet == contours[right].source_sheet and contours[left].source_handle != contours[right].source_handle)
    return sum(1 for index, first in enumerate(contours) for second in contours[index + 1:] if first.source_sheet == second.source_sheet and first.source_handle != second.source_handle and _crossing(first, second))
