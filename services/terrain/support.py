from __future__ import annotations

import math

from .contracts import Bounds, ConstraintSet


def summarize_support(constraints: ConstraintSet, bounds: Bounds) -> dict[str, float | int]:
    contour_length = sum(
        math.dist(a, b)
        for item in constraints.contours
        for a, b in zip(item.geometry, item.geometry[1:])
    )
    area_km2 = max((bounds.east - bounds.west) * (bounds.north - bounds.south) / 1_000_000.0, 1e-12)
    return {
        "contour_count": len(constraints.contours),
        "spot_height_count": len(constraints.spot_heights),
        "valid_constraint_count": len(constraints.contours) + len(constraints.spot_heights),
        "contour_length_m": round(contour_length, 6),
        "contour_length_km_per_km2": round(contour_length / 1000.0 / area_km2, 6),
        "spot_height_density_per_km2": round(len(constraints.spot_heights) / area_km2, 6),
        "bounds_m": {"west": bounds.west, "south": bounds.south, "east": bounds.east, "north": bounds.north},
    }

