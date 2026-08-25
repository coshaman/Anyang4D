from __future__ import annotations

import importlib.util
import json
import math
import shutil
import time
import tracemalloc
from pathlib import Path

import numpy as np
from pyproj import Transformer

from services.terrain.contracts import Bounds, ConstraintSet
from services.terrain.dxf import extract_constraints
from services.terrain.rescue import build_contour_aware_surface, predict_contour_aware
from services.terrain.rescue_decision import decide_rescue
from services.terrain.support import summarize_support
from services.terrain.topology import audit_contour_topology
from services.terrain.validation import classify_quality, elevation_metrics, terrain_diagnostics
from scripts.evals.goal3d_terrain import (
    AOI_WGS84, ROOT, RASTER_DIR, _decimate, _expanded, _points, _projected_bounds, _remove_blocks, _road_support, _sheet, _write_raster,
)

OUT = ROOT / "artifacts/evals/terrain/goal3dr"


def _remove_contour_blocks(contours, held_points, block_size_m=25.0):
    blocked = {((math.floor(x / block_size_m)), (math.floor(y / block_size_m))) for x, y in held_points}
    return [item for item in contours if not any((math.floor(x / block_size_m), math.floor(y / block_size_m)) in blocked for x, y in item.geometry)]


def _spot_metrics(constraints: ConstraintSet, held_spots) -> dict[str, object]:
    actual, predicted = [], []
    for held in held_spots:
        held_point = held.geometry[0]
        contours = _remove_contour_blocks(constraints.contours, {held_point})
        train = ConstraintSet(constraints.source_path, constraints.source_sha256, constraints.sheet_number, contours, [])
        actual.append(held.elevation_m)
        predicted.append(float(predict_contour_aware(train, [held_point])[0]))
    return elevation_metrics(np.asarray(actual), np.asarray(predicted))


def _contour_metrics(constraints: ConstraintSet, held_contours) -> dict[str, object]:
    actual, predicted = [], []
    for held in held_contours:
        held_points = set(held.geometry)
        contours = [item for item in _remove_contour_blocks(constraints.contours, held_points) if item.source_handle != held.source_handle]
        train = ConstraintSet(constraints.source_path, constraints.source_sha256, constraints.sheet_number, contours, [])
        sample = held.geometry[:: max(1, len(held.geometry) // 10)]
        values = predict_contour_aware(train, list(sample))
        actual.extend([held.elevation_m] * len(sample))
        predicted.extend(values.tolist())
    return elevation_metrics(np.asarray(actual), np.asarray(predicted))


def _seam(constraints_by_tile: list[ConstraintSet], bounds: Bounds) -> dict[str, object]:
    if len(constraints_by_tile) < 2:
        return {"count": 0, "median_m": math.inf, "p95_m": math.inf}
    x_boundary = Transformer.from_crs("EPSG:4326", "EPSG:5186", always_xy=True).transform(126.95, 37.386)[0]
    ys = np.linspace(bounds.south, bounds.north, 100)
    left = ConstraintSet(constraints_by_tile[0].source_path, "", "", constraints_by_tile[0].contours, [])
    right = ConstraintSet(constraints_by_tile[1].source_path, "", "", constraints_by_tile[1].contours, [])
    differences = np.abs(predict_contour_aware(left, [(x_boundary, y) for y in ys]) - predict_contour_aware(right, [(x_boundary, y) for y in ys]))
    return {"count": int(len(differences)), "median_m": float(np.median(differences)), "p95_m": float(np.percentile(differences, 95))}


def _method_b_status() -> dict[str, object]:
    grass = shutil.which("grass") or shutil.which("grass84") or shutil.which("grass83")
    qgis = shutil.which("qgis_process")
    scipy = importlib.util.find_spec("scipy") is not None
    if grass:
        return {"status": "AVAILABLE_NOT_RUN", "executable": grass, "reason": "bounded rescue runner did not invoke external GIS process automatically"}
    return {"status": "METHOD_B_NOT_RUN", "grass_available": False, "qgis_process_available": bool(qgis), "scipy_available": scipy, "reason": "GRASS/QGIS RST implementation and a compatible spline backend are unavailable in the current isolated environment; no unverified spline substitute was introduced"}


def _method_c_status() -> dict[str, object]:
    return {"status": "METHOD_C_NOT_RUN", "reason": "no reliable constrained-TIN implementation is installed; ordinary unconstrained triangulation would not preserve isoline breaklines"}


def _contour_assumption_flags(topology: dict[str, object], spot_count: int) -> dict[str, object]:
    dangling = int(topology["dangling_endpoint_count"])
    return {
        "discontinuous_contour_warning": dangling > 0,
        "dangling_endpoint_count": dangling,
        "contours_not_extending_warning": dangling > 0,
        "spot_elevations_between_contours": spot_count > 0,
        "crossing_warning": int(topology["crossing_pair_count"]) > 0,
        "duplicated_contour_warning": int(topology["duplicate_geometry_count"]) > 0,
    }


def main() -> None:
    started = time.perf_counter()
    tracemalloc.start()
    bounds = _projected_bounds()
    extraction_bounds = _expanded(bounds, 500)
    dxf_files = sorted((ROOT / "docs").glob("(B010)*.dxf"))
    sets = [extract_constraints(path, _sheet(path), extraction_bounds) for path in dxf_files]
    topology = audit_contour_topology(sets)
    combined = ConstraintSet(ROOT / "docs" / "2025-ngii-topographic-dxf-set", "composite:" + ",".join(item.source_sha256 for item in sets), "composite", [item for result in sets for item in result.contours], [item for result in sets for item in result.spot_heights], sum(item.rejected_entity_count for item in sets))
    baseline_working = _decimate(combined)
    working = ConstraintSet(combined.source_path, combined.source_sha256, combined.sheet_number, combined.contours, baseline_working.spot_heights, combined.rejected_entity_count)
    held_spots = baseline_working.spot_heights[:100]
    held_contours = baseline_working.contours[:20]
    topology["assumption_flags"] = _contour_assumption_flags(topology, len(working.spot_heights))
    topology["holdout"] = {"spot_ids": [item.source_handle for item in held_spots], "contour_ids": [item.source_handle for item in held_contours], "spatial_block_m": 25.0}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "contour-topology.json").write_text(json.dumps(topology, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Point holdouts remain at their exact source coordinates; the diagnostic
    # rescue raster uses a bounded 10 m grid to keep the isoline-distance
    # evaluation computationally tractable.
    surface = build_contour_aware_surface(working, bounds, 10.0)
    spot = _spot_metrics(working, held_spots)
    contour = _contour_metrics(working, held_contours)
    seam = _seam(sets, bounds)
    road = _road_support(working, bounds)
    diagnostics = terrain_diagnostics(surface.elevation, surface.grid_spacing_m)
    report = {
        "method": "contour_aware_distance",
        "method_principle": "nearest lower/upper distinct contour isolines; interpolate by true point-to-isoline distance without treating contour vertices as independent observations",
        "source_year": 2025,
        "source_crs": "EPSG:5186",
        "provenance": "DERIVED_TERRAIN_FROM_TOPOGRAPHIC_VECTORS",
        "grid_spacing_m": 10.0,
        "spot_holdout": spot,
        "contour_holdout": contour,
        "contour_holdout_p95_m": contour["p95_abs_error_m"],
        "seam": seam,
        "seam_p95_m": seam["p95_m"],
        "seam_median_m": seam["median_m"],
        "road_support": road,
        "road_p95_m": road["p95_m"],
        "coverage": diagnostics["coverage_fraction"],
        "slope_p99": diagnostics["slope_p99"],
        "diagnostics": diagnostics,
        "quality_class": classify_quality({"spot": spot, "contour_p95_m": contour["p95_abs_error_m"], "seam_p95_m": seam["p95_m"], "seam_median_m": seam["median_m"], "road_p95_m": road["p95_m"], "coverage": diagnostics["coverage_fraction"], "slope_p99": diagnostics["slope_p99"]}),
        "authorization": {"flood_simulation": False, "hazard_frames": False, "citizen_routing": False},
        "runtime_seconds": time.perf_counter() - started,
        "peak_traced_memory_mb": tracemalloc.get_traced_memory()[1] / 1024 / 1024,
        "raster": _write_raster(surface, bounds, OUT / "contour" / "terrain.tif"),
    }
    (OUT / "contour" ).mkdir(parents=True, exist_ok=True)
    (OUT / "contour" / "quality.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    baseline = json.loads((ROOT / "artifacts/evals/terrain/goal3dr/baseline-goal3d.json").read_text(encoding="utf-8"))
    comparison = {
        "frozen_validation_plan_sha256": "72333c5a496c1f7abdf75ef567e22cea1c92d0944a7ae0103e6cdf830d808466",
        "holdout_identity": topology["holdout"],
        "methods": [
            {"method": "idw_power_2_baseline", "source": "baseline-goal3d.json", "spot": baseline["spot_holdout"], "contour": baseline["contour_holdout"], "seam": baseline["seam"], "road_support": baseline["road_support"], "sink_cell_count": None, "runtime_seconds": None, "peak_memory_mb": None, "terrain_class": baseline["quality_class"]},
            {"method": "contour_aware_distance", "spot": report["spot_holdout"], "contour": report["contour_holdout"], "seam": report["seam"], "road_support": report["road_support"], "sink_cell_count": diagnostics["sink_cell_count"], "runtime_seconds": report["runtime_seconds"], "peak_memory_mb": report["peak_traced_memory_mb"], "terrain_class": report["quality_class"]},
            {"method": "rst", "status": _method_b_status(), "terrain_class": "METHOD_B_NOT_RUN"},
            {"method": "constrained_tin", "status": _method_c_status(), "terrain_class": "METHOD_C_NOT_RUN"},
        ],
        "selection": "contour_aware_distance evaluated but not promoted unless frozen TERRAIN_B/A gate passes",
    }
    (OUT / "method-comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    decision = decide_rescue({"baseline": baseline["quality_class"], "contour": report["quality_class"]})
    decision.update({"canonical_terrain_decision": "KEEP_EXISTING_AS_FAILED_DIAGNOSTIC_ONLY", "contour_method_quality": report["quality_class"], "no_further_terrain_rescue": True})
    (OUT / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"topology": topology, "contour": report, "comparison": comparison, "decision": decision}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
