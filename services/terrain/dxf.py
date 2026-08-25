from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from .contracts import Bounds, ConstraintSet, DxfLayerAudit, ElevationConstraint

CONTOUR_LAYERS = frozenset({"F0017111", "F0017114"})
SPOT_HEIGHT_LAYERS = frozenset({"F0027217"})


def _pairs(path: Path) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="cp949", errors="replace").splitlines()
    if len(lines) % 2:
        lines = lines[:-1]
    return [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines), 2)]


def _entities(path: Path) -> list[dict[str, list[str]]]:
    found: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] | None = None
    for code, value in _pairs(path):
        if code == "0":
            if current and current.get("type", [""])[0] not in {"SECTION", "ENDSEC", "EOF"}:
                found.append(current)
            current = {"type": [value]}
        elif current is not None:
            current.setdefault(code, []).append(value)
    return found


def _number(values: list[str], index: int = 0) -> float | None:
    try:
        return float(values[index])
    except (IndexError, TypeError, ValueError):
        return None


def _vertices(entity: dict[str, list[str]]) -> tuple[tuple[float, float], ...]:
    xs, ys = entity.get("10", []), entity.get("20", [])
    return tuple((x, y) for x, y in zip((_number(xs, i) for i in range(len(xs))), (_number(ys, i) for i in range(len(ys)))) if x is not None and y is not None)


def audit_dxf_layers(path: Path) -> DxfLayerAudit:
    entities = _entities(path)
    layers = Counter(entity.get("8", [""])[0] for entity in entities)
    types = Counter(entity.get("type", [""])[0] for entity in entities)
    contour_layers = sorted({entity.get("8", [""])[0] for entity in entities if entity.get("type", [""])[0] == "LWPOLYLINE" and entity.get("38") and len(_vertices(entity)) >= 2})
    point_layers = sorted({entity.get("8", [""])[0] for entity in entities if entity.get("type", [""])[0] == "INSERT" and entity.get("30") and _number(entity.get("30", [])) is not None})
    return DxfLayerAudit(len(entities), dict(layers), dict(types), tuple(contour_layers), tuple(point_layers))


def extract_constraints(path: Path, sheet_number: str, bounds: Bounds) -> ConstraintSet:
    if not (sheet_number.isdigit() and len(sheet_number) == 8):
        raise ValueError("sheet_number must be an 8-digit map sheet number")
    contours: list[ElevationConstraint] = []
    spots: list[ElevationConstraint] = []
    rejected = 0
    seen: set[tuple[str, str, str, float, tuple[tuple[float, float], ...]]] = set()
    for entity in _entities(path):
        kind = entity.get("type", [""])[0]
        layer = entity.get("8", [""])[0]
        handle = entity.get("5", [""])[0]
        geometry: tuple[tuple[float, float], ...]
        elevation: float | None
        target: list[ElevationConstraint] | None
        if kind == "LWPOLYLINE" and layer in CONTOUR_LAYERS:
            geometry = _vertices(entity)
            elevation = _number(entity.get("38", []))
            target = contours
            if len(geometry) < 2 or elevation is None or not bounds.intersects([p[0] for p in geometry], [p[1] for p in geometry]):
                continue
        elif kind == "INSERT" and layer in SPOT_HEIGHT_LAYERS:
            geometry = _vertices(entity)[:1]
            elevation = _number(entity.get("30", []))
            target = spots
            if not geometry or elevation is None or not bounds.contains(*geometry[0]):
                continue
        else:
            if kind in {"LWPOLYLINE", "INSERT"}:
                rejected += 1
            continue
        key = (sheet_number, layer, handle, elevation, geometry)
        if key in seen:
            continue
        seen.add(key)
        target.append(ElevationConstraint(sheet_number, layer, handle, "contour" if target is contours else "spot_height", elevation, geometry))
    return ConstraintSet(path, hashlib.sha256(path.read_bytes()).hexdigest(), sheet_number, contours, spots, rejected)

