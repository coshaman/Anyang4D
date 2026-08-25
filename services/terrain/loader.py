from __future__ import annotations

import json
from pathlib import Path


def validate_terrain_metadata(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("provenance") != "DERIVED_TERRAIN_FROM_TOPOGRAPHIC_VECTORS":
        raise ValueError("terrain provenance is not authoritative vector-derived terrain")
    if payload.get("source_crs") != "EPSG:5186":
        raise ValueError("terrain CRS must be EPSG:5186")
    authorization = payload.get("authorization", {})
    if authorization.get("flood_simulation"):
        raise ValueError("terrain artifact cannot authorize flood simulation")
    if authorization.get("hazard_frames") or authorization.get("citizen_routing"):
        raise ValueError("terrain artifact cannot authorize downstream public-safety claims")
    return payload

