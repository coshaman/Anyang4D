from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

from pyproj import Transformer

from .dem_metadata import parse_grid_interval_m


ROOT = Path(__file__).resolve().parents[2]
AOI_WIDTH_DEG = 0.02
AOI_HEIGHT_DEG = 0.02


def _inside(point: tuple[float, float], bbox: tuple[float, float, float, float]) -> bool:
    lat, lon = point
    lat_min, lon_min, lat_max, lon_max = bbox
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


def _bbox_sheets(bbox: tuple[float, float, float, float], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    lat_min, lon_min, lat_max, lon_max = bbox
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5174", always_xy=True)
    x1, y1 = transformer.transform(lon_min, lat_min)
    x2, y2 = transformer.transform(lon_max, lat_max)
    ax, bx, ay, by = min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)
    selected = []
    for row in rows:
        if "안양" not in (row.get("도엽명5000") or ""):
            continue
        if parse_grid_interval_m(row.get("격자간격")) != 1.0 or (row.get("원시자료제작년도") or "").strip() != "2009":
            continue
        try:
            rx1 = float(row["원시좌하단의평면X좌표"])
            ry1 = float(row["원시좌하단의평면Y좌표"])
            rx2 = float(row["원시우상단의평면X좌표"])
            ry2 = float(row["원시우상단의평면Y좌표"])
        except (KeyError, ValueError):
            continue
        if rx1 <= bx and rx2 >= ax and ry1 <= by and ry2 >= ay:
            selected.append({
                "sheet_name": row["도엽명5000"].strip(),
                "sheet_id": row["도엽번호5000"].strip(),
                "grid_interval_m": 1.0,
                "recorded_grid_interval": row["격자간격"].strip(),
                "production_year": row["원시자료제작년도"].strip(),
                "crs": (row.get("좌표계") or "").strip() or None,
                "vertical_datum": (row.get("표고기준") or "").strip() or None,
                "data_format": (row.get("자료형식") or "").strip() or None,
                "accuracy": (row.get("정확도") or "").strip() or None,
            })
    unique: dict[str, dict[str, Any]] = {}
    for record in selected:
        unique.setdefault(record["sheet_id"], record)
    return list(unique.values())


def select_demo_aoi(output_path: Path | None = None) -> dict[str, Any]:
    output_path = output_path or ROOT / "artifacts/evals/data/demo-aoi.geojson"
    facilities = json.loads((ROOT / "data/processed/anyang_facilities.json").read_text(encoding="utf-8"))["records"]
    shelters = [(record["latitude"], record["longitude"]) for record in facilities if record.get("category") == "CIVIL_DEFENSE_SHELTER" and record.get("latitude") and 37.30 < record["latitude"] < 37.50 and 126.85 < record["longitude"] < 127.05]
    water = [(record["latitude"], record["longitude"]) for record in facilities if record.get("category") == "EMERGENCY_WATER" and record.get("latitude") and 37.30 < record["latitude"] < 37.50 and 126.85 < record["longitude"] < 127.05]
    osm = json.loads((ROOT / "data/raw/openstreetmap/anyang_pedestrian_broad/overpass.json").read_text(encoding="utf-8"))
    nodes = [(element.get("lat"), element.get("lon")) for element in osm["elements"] if element["type"] == "node" and element.get("lat") and element.get("lon")]
    node_bins: dict[tuple[int, int], int] = {}
    for lat, lon in nodes:
        key = (math.floor(lat / 0.005), math.floor(lon / 0.005))
        node_bins[key] = node_bins.get(key, 0) + 1
    with (ROOT / "data/raw/ngii/dem_metadata_20231107.csv").open(encoding="cp949", newline="") as handle:
        metadata = [
            row for row in csv.DictReader(handle)
            if "안양" in (row.get("도엽명5000") or "")
            and parse_grid_interval_m(row.get("격자간격")) == 1.0
            and (row.get("원시자료제작년도") or "").strip() == "2009"
        ]
    candidates = []
    for lat_i in range(37350, 37451, 2):
        for lon_i in range(126900, 127001, 2):
            lat, lon = lat_i / 1000, lon_i / 1000
            bbox = (lat - AOI_HEIGHT_DEG / 2, lon - AOI_WIDTH_DEG / 2, lat + AOI_HEIGHT_DEG / 2, lon + AOI_WIDTH_DEG / 2)
            sheets = _bbox_sheets(bbox, metadata)
            if not sheets:
                continue
            shelter_count = sum(_inside(point, bbox) for point in shelters)
            water_count = sum(_inside(point, bbox) for point in water)
            node_count = sum(
                node_bins.get((bin_lat, bin_lon), 0)
                for bin_lat in range(math.floor(bbox[0] / 0.005), math.floor(bbox[2] / 0.005) + 1)
                for bin_lon in range(math.floor(bbox[1] / 0.005), math.floor(bbox[3] / 0.005) + 1)
            )
            score = shelter_count * 10 + water_count * 3 + node_count / 1000 - abs(len(sheets) - 2) * 4
            candidates.append((score, bbox, sheets, shelter_count, water_count, node_count))
    if not candidates:
        raise RuntimeError("no compact candidate overlaps a recorded 1 m Anyang sheet")
    score, bbox, sheets, shelter_count, water_count, node_count = max(candidates, key=lambda item: item[0])
    lat_min, lon_min, lat_max, lon_max = bbox
    geojson = {
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {"name": "Anyang central dense-network demo AOI", "provenance": "SELECTION_ONLY", "score": round(score, 3), "shelter_count": shelter_count, "water_count": water_count, "osm_node_count": node_count}, "geometry": {"type": "Polygon", "coordinates": [[[lon_min, lat_min], [lon_max, lat_min], [lon_max, lat_max], [lon_min, lat_max], [lon_min, lat_min]]]}}],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"bbox": bbox, "score": round(score, 3), "sheet_count": len(sheets), "sheets": sheets, "shelter_count": shelter_count, "water_count": water_count, "osm_node_count": node_count, "geojson_path": output_path.as_posix()}


if __name__ == "__main__":
    print(json.dumps(select_demo_aoi(), ensure_ascii=False, indent=2))
