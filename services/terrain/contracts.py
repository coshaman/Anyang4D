from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Bounds:
    west: float
    south: float
    east: float
    north: float

    def __post_init__(self) -> None:
        if self.east < self.west or self.north < self.south:
            raise ValueError("bounds must be ordered west<=east and south<=north")

    def contains(self, x: float, y: float) -> bool:
        return self.west <= x <= self.east and self.south <= y <= self.north

    def intersects(self, xs: list[float], ys: list[float]) -> bool:
        return not (max(xs) < self.west or min(xs) > self.east or max(ys) < self.south or min(ys) > self.north)


@dataclass(frozen=True)
class ElevationConstraint:
    source_sheet: str
    source_layer: str
    source_handle: str
    kind: str
    elevation_m: float
    geometry: tuple[tuple[float, float], ...]

    @property
    def x(self) -> float:
        return self.geometry[0][0]

    @property
    def y(self) -> float:
        return self.geometry[0][1]


@dataclass(frozen=True)
class ConstraintSet:
    source_path: Path
    source_sha256: str
    sheet_number: str
    contours: list[ElevationConstraint] = field(default_factory=list)
    spot_heights: list[ElevationConstraint] = field(default_factory=list)
    rejected_entity_count: int = 0


@dataclass(frozen=True)
class DxfLayerAudit:
    entity_count: int
    layer_counts: dict[str, int]
    entity_type_counts: dict[str, int]
    candidate_contour_layers: tuple[str, ...]
    candidate_point_layers: tuple[str, ...]

