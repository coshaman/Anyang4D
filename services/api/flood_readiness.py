from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter


ROOT = Path(__file__).resolve().parents[2]
router = APIRouter(prefix="/api/admin/flood-readiness", tags=["admin-flood-readiness"])


@router.get("")
def flood_readiness() -> dict:
    quality_path = ROOT / "artifacts/evals/data/anyang-dem-supplied-quality.json"
    if quality_path.exists():
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
    else:
        quality = {"source_count": 4, "unique_source_sha256": ["40873ee25879aa52ee6665f534f0083d3ab7ca1c21bbaf5ad7aa7f3dff954598"], "duplicate_source_bytes": True, "records": [{"res": [90.0, 90.0], "driver": "HFA", "crs": "EPSG:5179"}]}
    first = quality["records"][0]
    return {
        "status": "CLOSED_NOT_RELEASE_DEPENDENCY",
        "source_year": 2025,
        "source_count": quality["source_count"],
        "unique_source_count": len(quality["unique_source_sha256"]),
        "duplicate_source_bytes": quality["duplicate_source_bytes"],
        "native_resolution_m": first["res"][0],
        "native_format": first["driver"],
        "native_crs": first["crs"],
        "high_res_terrain_acquisition": "CLOSED",
        "real_level_a_authorized": False,
        "admin_scenario_authorized": True,
        "citizen_routing_authorized": False,
        "terrain_dependency_for_release": False,
        "terrain_quality_class": "TERRAIN_C",
        "role": "COARSE_TERRAIN_CONTEXT_ONLY",
        "reason": "The supplied ZIPs are duplicate 90m rasters. The street-level terrain-flood research branch is permanently closed and is not a release dependency.",
        "forbidden_uses": ["street-level flood calculation", "water depth", "flood probability", "road safety inference", "citizen routing", "road closure inference", "building-level hazard", "shelter safety inference"],
    }
