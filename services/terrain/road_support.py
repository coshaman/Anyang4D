from __future__ import annotations

import math


def nearest_constraint_distance(points: list[tuple[float, float]], location: tuple[float, float]) -> float:
    if not points:
        return math.inf
    return min(math.hypot(x - location[0], y - location[1]) for x, y in points)

