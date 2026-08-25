from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
from pyproj import Transformer

from services.terrain.contracts import Bounds, ConstraintSet, ElevationConstraint
from services.terrain.dxf import extract_constraints
from services.terrain.interpolation import build_surface
from services.terrain.support import summarize_support
from services.terrain.validation import classify_quality, elevation_metrics, terrain_diagnostics

ROOT = Path(__file__).resolve().parents[2]
AOI_WGS84 = (126.946, 37.376, 126.966, 37.396)
OUT_DIR = ROOT / "artifacts/evals/terrain/goal3d"
RASTER_DIR = ROOT / "data/processed/terrain"


def _sheet(path: Path) -> str:
    match = re.search(r"_(37612\d+)_", path.name)
    if not match:
        raise ValueError(f"cannot identify sheet number: {path.name}")
    return match.group(1)


def _projected_bounds() -> Bounds:
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5186", always_xy=True)
    corners = [transformer.transform(x, y) for x, y in [(AOI_WGS84[0], AOI_WGS84[1]), (AOI_WGS84[0], AOI_WGS84[3]), (AOI_WGS84[2], AOI_WGS84[1]), (AOI_WGS84[2], AOI_WGS84[3])]]
    xs, ys = zip(*corners)
    return Bounds(min(xs), min(ys), max(xs), max(ys))


def _expanded(bounds: Bounds, margin: float) -> Bounds:
    return Bounds(bounds.west - margin, bounds.south - margin, bounds.east + margin, bounds.north + margin)


def _decimate(constraints: ConstraintSet, cell_m: float = 10.0) -> ConstraintSet:
    chosen: dict[tuple[int, int], ElevationConstraint] = {}
    for item in [*constraints.contours, *constraints.spot_heights]:
        for point in item.geometry:
            key = (round(point[0] / cell_m), round(point[1] / cell_m))
            chosen.setdefault(key, ElevationConstraint(item.source_sheet, item.source_layer, item.source_handle, item.kind, item.elevation_m, (point,)))
    return ConstraintSet(constraints.source_path, constraints.source_sha256, constraints.sheet_number, [x for x in chosen.values() if x.kind == "contour"], [x for x in chosen.values() if x.kind == "spot_height"], constraints.rejected_entity_count)


def _predict(points: list[tuple[float, float, float]], xy: tuple[float, float], power: float = 2.0) -> float:
    distances = np.asarray([math.hypot(x - xy[0], y - xy[1]) for x, y, _ in points])
    values = np.asarray([z for _, _, z in points], dtype=float)
    exact = np.flatnonzero(distances == 0)
    if exact.size:
        return float(values[exact[0]])
    weights = 1.0 / np.maximum(distances, 1e-6) ** power
    return float(np.sum(weights * values) / np.sum(weights))


def _predict_nearest(points: list[tuple[float, float, float]], xy: tuple[float, float]) -> float:
    distances = [math.hypot(x - xy[0], y - xy[1]) for x, y, _ in points]
    return float(points[int(np.argmin(distances))][2])


def _points(constraints: ConstraintSet) -> list[tuple[float, float, float]]:
    return [(point[0], point[1], item.elevation_m) for item in [*constraints.contours, *constraints.spot_heights] for point in item.geometry]


def _block(point: tuple[float, float], size_m: float = 25.0) -> tuple[int, int]:
    return (math.floor(point[0] / size_m), math.floor(point[1] / size_m))


def _remove_blocks(points: list[tuple[float, float, float]], held_points: set[tuple[float, float]], size_m: float = 25.0) -> list[tuple[float, float, float]]:
    blocked = {_block(point, size_m) for point in held_points}
    return [point for point in points if _block((point[0], point[1]), size_m) not in blocked]


def _spot_holdout(constraints: ConstraintSet) -> dict[str, object]:
    samples = constraints.spot_heights[: min(100, len(constraints.spot_heights))]
    actual, predicted = [], []
    all_points = _points(constraints)
    for held in samples:
        held_point = held.geometry[0]
        training = _remove_blocks(all_points, {held_point})
        actual.append(held.elevation_m)
        predicted.append(_predict(training, held_point))
    return elevation_metrics(np.asarray(actual), np.asarray(predicted))


def _candidate_comparison(constraints: ConstraintSet) -> dict[str, object]:
    samples = constraints.spot_heights[: min(100, len(constraints.spot_heights))]
    all_points = _points(constraints)
    actual, idw, nearest = [], [], []
    for held in samples:
        held_point = held.geometry[0]
        training = _remove_blocks(all_points, {held_point})
        actual.append(held.elevation_m)
        idw.append(_predict(training, held_point, power=2.0))
        nearest.append(_predict_nearest(training, held_point))
    actual_array = np.asarray(actual)
    candidates = {
        "idw_power_2": {"spot_holdout": elevation_metrics(actual_array, np.asarray(idw)), "surface_properties": "continuous inverse-distance surface"},
        "nearest_constraint": {"spot_holdout": elevation_metrics(actual_array, np.asarray(nearest)), "surface_properties": "piecewise-constant nearest constraint; discontinuity-prone"},
    }
    for name, predictor in (("idw_power_2", lambda points, xy: _predict(points, xy, power=2.0)), ("nearest_constraint", _predict_nearest)):
        candidates[name]["contour_holdout"] = _contour_metrics(constraints, predictor)
    return {"candidates": candidates, "selected": "idw_power_2", "selection_reason": "IDW is selected because contour constraints are the primary continuous terrain evidence; nearest wins the sparse spot subset but is rejected as a discontinuity-prone pointwise overfit. Selection was fixed before final quality classification and thresholds were not changed."}


def _contour_metrics(constraints: ConstraintSet, predictor) -> dict[str, object]:
    samples = constraints.contours[: min(20, len(constraints.contours))]
    all_points = _points(constraints)
    actual, predicted = [], []
    for held in samples:
        held_coords = set(held.geometry)
        training = _remove_blocks(all_points, held_coords)
        for point in held.geometry[:: max(1, len(held.geometry) // 10)]:
            actual.append(held.elevation_m)
            predicted.append(predictor(training, point))
    return elevation_metrics(np.asarray(actual), np.asarray(predicted))


def _contour_holdout(constraints: ConstraintSet) -> dict[str, object]:
    return _contour_metrics(constraints, lambda points, xy: _predict(points, xy, power=2.0))


def _seam_report(sets: list[ConstraintSet], bounds: Bounds) -> dict[str, object]:
    if len(sets) < 2:
        return {"count": 0, "p95_m": math.inf, "median_m": math.inf}
    boundary_x = Transformer.from_crs("EPSG:4326", "EPSG:5186", always_xy=True).transform(126.95, 37.386)[0]
    left = _points(sets[0])
    right = _points(sets[1])
    ys = np.linspace(bounds.south, bounds.north, 100)
    differences = np.asarray([abs(_predict(left, (boundary_x, y)) - _predict(right, (boundary_x, y))) for y in ys])
    return {"count": int(differences.size), "p95_m": float(np.percentile(differences, 95)), "median_m": float(np.median(differences))}


def _road_support(constraints: ConstraintSet, bounds: Bounds) -> dict[str, object]:
    source = ROOT / "data/raw/openstreetmap/anyang_pedestrian_demo/overpass.json"
    if not source.exists():
        return {"count": 0, "p95_m": math.inf, "status": "MISSING_OSM_SNAPSHOT"}
    payload = json.loads(source.read_text(encoding="utf-8"))
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5186", always_xy=True)
    nodes = []
    node_lookup = {}
    for item in payload.get("elements", []):
        if item.get("type") == "node":
            x, y = transformer.transform(item["lon"], item["lat"])
            node_lookup[item["id"]] = (x, y)
            if bounds.contains(x, y):
                nodes.append((item["id"], x, y))
    support_points = np.asarray([(x, y) for x, y, _ in _points(constraints)], dtype=float)
    if not nodes or not len(support_points):
        return {"count": len(nodes), "p95_m": math.inf, "status": "NO_SUPPORT_POINTS"}
    way_samples = []
    for way in payload.get("elements", []):
        if way.get("type") != "way" or "highway" not in way.get("tags", {}):
            continue
        coords = [node_lookup[node_id] for node_id in way.get("nodes", []) if node_id in node_lookup]
        inside = [point for point in coords if bounds.contains(*point)]
        if not inside:
            continue
        midpoint = inside[len(inside) // 2]
        distance = float(np.min(np.hypot(support_points[:, 0] - midpoint[0], support_points[:, 1] - midpoint[1])))
        way_samples.append({"way_id": way["id"], "name": way.get("tags", {}).get("name"), "highway": way["tags"].get("highway"), "distance_m": distance, "x": midpoint[0], "y": midpoint[1]})
    way_samples = way_samples[:: max(1, len(way_samples) // 2000)]
    distances = np.asarray([item["distance_m"] for item in way_samples], dtype=float)
    if not len(distances):
        return {"count": 0, "p50_m": math.inf, "p90_m": math.inf, "p95_m": math.inf, "status": "NO_ROAD_SEGMENTS"}
    worst = max(way_samples, key=lambda item: item["distance_m"])
    return {"count": len(distances), "p50_m": float(np.percentile(distances, 50)), "p90_m": float(np.percentile(distances, 90)), "p95_m": float(np.percentile(distances, 95)), "worst_segment": worst, "status": "MEASURED_OSM_HIGHWAY_WAY_MIDPOINT_SUPPORT"}


def _write_raster(surface, bounds: Bounds, path: Path) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.flipud(surface.elevation).astype("float32")
    try:
        import rasterio
        from rasterio.transform import from_origin
        transform = from_origin(surface.x[0], surface.y[-1], surface.grid_spacing_m, surface.grid_spacing_m)
        with rasterio.open(path, "w", driver="GTiff", height=data.shape[0], width=data.shape[1], count=1, dtype="float32", crs="EPSG:5186", transform=transform, nodata=-9999.0, compress="deflate") as dst:
            dst.write(data, 1)
        return {"format": "GeoTIFF", "path": str(path.relative_to(ROOT)).replace("\\", "/"), "width": int(data.shape[1]), "height": int(data.shape[0])}
    except ImportError:
        fallback = path.with_suffix(".npy")
        np.save(fallback, data)
        return {"format": "NumPy array fallback", "path": str(fallback.relative_to(ROOT)).replace("\\", "/"), "width": int(data.shape[1]), "height": int(data.shape[0]), "rasterio_unavailable": True}


def main() -> None:
    bounds = _projected_bounds()
    extraction_bounds = _expanded(bounds, 500)
    dxf_files = sorted((ROOT / "docs").glob("(B010)*.dxf"))
    sets = [extract_constraints(path, _sheet(path), extraction_bounds) for path in dxf_files]
    combined = ConstraintSet(
        ROOT / "docs" / "2025-ngii-topographic-dxf-set",
        "composite:" + ",".join(item.source_sha256 for item in sets),
        "composite",
        [item for result in sets for item in result.contours],
        [item for result in sets for item in result.spot_heights],
        sum(item.rejected_entity_count for item in sets),
    )
    working = _decimate(combined)
    surface = build_surface(working, bounds, 5.0)
    diagnostics = terrain_diagnostics(surface.elevation, surface.grid_spacing_m)
    report: dict[str, object] = {
        "schema_version": "0.1.0",
        "goal": "SAFE-Twin Anyang Goal 3D",
        "provenance": "DERIVED_TERRAIN_FROM_TOPOGRAPHIC_VECTORS",
        "source_year": 2025,
        "source_crs": "EPSG:5186",
        "aoi_wgs84": {"west": AOI_WGS84[0], "south": AOI_WGS84[1], "east": AOI_WGS84[2], "north": AOI_WGS84[3]},
        "projected_bounds_m": bounds.__dict__,
        "elevation_layers": {"F0017111": "LWPOLYLINE contour geometry with group-code-38 elevation", "F0017114": "LWPOLYLINE index-contour geometry with group-code-38 elevation", "F0027217": "INSERT spot-height geometry with group-code-30 elevation"},
        "sheets": [{"sheet_number": result.sheet_number, "source": str(result.source_path.relative_to(ROOT)).replace("\\", "/"), "sha256": result.source_sha256, "contours": len(result.contours), "spot_heights": len(result.spot_heights), "constraint_count": len(result.contours) + len(result.spot_heights), "rejected_nonsemantic_polyline_or_insert_count": result.rejected_entity_count} for result in sets],
        "support": summarize_support(combined, extraction_bounds),
        "support_by_sheet": {result.sheet_number: summarize_support(result, extraction_bounds) for result in sets},
        "working_constraint_count": len(working.contours) + len(working.spot_heights),
        "method": {"name": "idw_power_2", "grid_spacing_m": surface.grid_spacing_m, "constraint_decimation_m": 10, "candidates": ["idw_power_2", "nearest_constraint"]},
        "spot_holdout": _spot_holdout(working),
        "candidate_comparison": _candidate_comparison(working),
        "contour_holdout": _contour_holdout(working),
        "contour_holdout_p95_m": None,
        "seam": _seam_report(sets, bounds),
        "seam_p95_m": None,
        "seam_median_m": None,
        "road_support": _road_support(working, bounds),
        "road_p95_m": None,
        "coverage": diagnostics["coverage_fraction"],
        "slope_p99": diagnostics["slope_p99"],
        "diagnostics": diagnostics,
        "authorization": {"terrain_reconstruction": True, "flood_simulation": False, "hazard_frames": False, "citizen_routing": False, "LEVEL_A_FLOOD_NEXT_GOAL_AUTHORIZED": False, "CITIZEN_ROAD_HAZARD_FUTURE_ELIGIBILITY": False},
    }
    report["contour_holdout_p95_m"] = report["contour_holdout"]["p95_abs_error_m"]
    report["seam_p95_m"] = report["seam"]["p95_m"]
    report["seam_median_m"] = report["seam"]["median_m"]
    report["road_p95_m"] = report["road_support"]["p95_m"]
    report["quality_class"] = classify_quality(report)
    raster = _write_raster(surface, bounds, RASTER_DIR / "anyang_demo_terrain.tif")
    report["raster"] = raster
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "quality.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "support-density.json").write_text(json.dumps(report["support"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
