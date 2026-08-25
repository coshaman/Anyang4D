from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AOI = (126.946, 37.376, 126.966, 37.396)
OUT = ROOT / "artifacts/evals/data/anyang-topographic-vector-audit.json"


def pairs(path: Path):
    lines = path.read_text(encoding="cp949", errors="replace").splitlines()
    return list(zip(lines[0::2], lines[1::2]))


def entities(path: Path) -> list[dict[str, list[str]]]:
    output = []
    current = None
    for code, value in pairs(path):
        code = code.strip()
        if code == "0":
            if current and current.get("type", [""])[0] not in {"SECTION", "ENDSEC", "EOF"}:
                output.append(current)
            current = {"type": [value.strip()]}
        elif current is not None:
            current.setdefault(code, []).append(value.strip())
    return output


def xml_texts(path: Path) -> list[str]:
    # The supplied ISO XML sidecars contain a few mismatched closing tags.
    # Preserve the bytes and extract character data without "repairing" the source.
    raw = path.read_text(encoding="utf-8", errors="replace")
    return [re.sub(r"<[^>]+>", "", text).strip() for text in re.findall(r">([^<>]+)<", raw) if text.strip()]


def xml_value(texts: list[str], pattern: str) -> str | None:
    for text in texts:
        if re.search(pattern, text):
            return text
    return None


def audit_file(dxf: Path, xml: Path) -> dict[str, object]:
    es = entities(dxf)
    layers = Counter(entity.get("8", [""])[0] for entity in es)
    types = Counter(entity.get("type", [""])[0] for entity in es)
    elevation_layers: dict[str, dict[str, object]] = {}
    for layer in sorted(set(layers)):
        layer_entities = [entity for entity in es if entity.get("8", [""])[0] == layer]
        contour_elevations = []
        point_elevations = []
        for entity in layer_entities:
            if "38" in entity:
                contour_elevations.extend(float(value) for value in entity["38"] if _number(value))
            if entity.get("type", [""])[0] == "INSERT" and "30" in entity:
                point_elevations.extend(float(value) for value in entity["30"] if _number(value))
        if contour_elevations or point_elevations:
            elevation_layers[layer] = {
                "entity_counts": dict(Counter(entity.get("type", [""])[0] for entity in layer_entities)),
                "contour_elevation_count": len(contour_elevations),
                "contour_elevation_values_m": sorted(set(contour_elevations)),
                "point_elevation_count": len(point_elevations),
                "point_elevation_range_m": [min(point_elevations), max(point_elevations)] if point_elevations else None,
            }

    texts = xml_texts(xml)
    bbox = _bbox(texts)
    return {
        "dxf": str(dxf.relative_to(ROOT)).replace("\\", "/"),
        "xml": str(xml.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(dxf.read_bytes()).hexdigest(),
        "bytes": dxf.stat().st_size,
        "sheet_number": re.search(r"_(37612\d+)_", dxf.name).group(1),
        "production_year": 2025,
        "format": "DXF",
        "crs": "EPSG:5186",
        "scale_denominator": 1000,
        "xml_bbox_wgs84": bbox,
        "aoi_intersects": _intersects(bbox, AOI),
        "entity_count": len(es),
        "entity_types": dict(types),
        "layer_count": len(layers),
        "top_layers": layers.most_common(20),
        "elevation_supporting_layers": elevation_layers,
        "elevation_support_summary": {
            "has_contour_polylines": any(value["contour_elevation_count"] for value in elevation_layers.values()),
            "has_elevation_points": any(value["point_elevation_count"] for value in elevation_layers.values()),
            "candidate_contour_layers": [layer for layer, value in elevation_layers.items() if value["contour_elevation_count"]],
            "candidate_point_layers": [
                layer for layer, value in elevation_layers.items()
                if value["point_elevation_count"] and any(
                    entity.get("type", [""])[0] == "INSERT"
                    and entity.get("8", [""])[0] == layer
                    and "30" in entity
                    for entity in es
                )
            ],
        },
        "xml_evidence": {
            "production_date": xml_value(texts, r"^2025-12-30$"),
            "survey_date": xml_value(texts, r"^2025-03-25$"),
            "title_fragment": next((text for text in texts if "도엽번호" in text), None),
            "restriction": next((text for text in texts if "재배포" in text), None),
        },
    }


def _number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _bbox(texts: list[str]) -> dict[str, float] | None:
    # XML values occur as standalone decimals in the fixed bbox order.
    values = []
    for text in texts:
        if re.fullmatch(r"-?\d+\.\d+", text):
            values.append(float(text))
    # First four geographic bbox values are the only values in the expected range.
    candidates = [value for value in values if 120 <= value <= 130 or 30 <= value <= 40]
    if len(candidates) < 4:
        return None
    return {"west": candidates[0], "east": candidates[1], "south": candidates[2], "north": candidates[3]}


def _intersects(bbox: dict[str, float] | None, aoi: tuple[float, float, float, float]) -> bool:
    if not bbox:
        return False
    west, south, east, north = aoi
    return bbox["west"] <= east and bbox["east"] >= west and bbox["south"] <= north and bbox["north"] >= south


def main() -> None:
    audits = []
    for dxf in sorted((ROOT / "docs").glob("(B010)*.dxf")):
        xml = dxf.with_suffix(".xml")
        audits.append(audit_file(dxf, xml))
    payload = {
        "schema_version": "0.1.0",
        "source": "user-supplied NGII 2025 1:1,000 digital topographic map DXF packages",
        "aoi_wgs84": {"west": AOI[0], "south": AOI[1], "east": AOI[2], "north": AOI[3]},
        "minimum_intersecting_sheets": [audit["sheet_number"] for audit in audits if audit["aoi_intersects"]],
        "audits": audits,
        "interpretation": {
            "current_official_vector_source": True,
            "not_a_dem": True,
            "candidate_elevation_layers": ["F0017111", "F0017114", "F0027217"],
            "terrain_derivation_status": "AUDIT_COMPLETE_DERIVATION_NOT_YET_RUN",
            "provenance_if_derived": "DERIVED_TERRAIN_FROM_TOPOGRAPHIC_VECTORS",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
