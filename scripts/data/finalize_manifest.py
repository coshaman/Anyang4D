from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/manifests/data_manifest.json"


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    datasets = []
    for record in payload["datasets"]:
        if record["id"] == "anyang-emergency-water":
            # This was a landing-page probe, not a source acquisition. The successful national file is retained below.
            continue
        if record["id"] == "emergency-water-national-standard":
            record.update({"crs": "EPSG:5174 for provider projected X/Y fields; no WGS84 fields present", "temporal_coverage": "provider snapshot; data 기준일자 field", "anyang_feature_count": 83})
        elif record["id"] == "civil-defense-shelter-national":
            record.update({"crs": "EPSG:4326 fields plus EPSG:5179 projected fields", "temporal_coverage": "provider snapshot; 데이터기준일자 field", "anyang_feature_count": 235})
        elif record["id"] == "aed-anyang-file":
            record.update({"crs": "not provided in file; no coordinates in downloaded schema", "temporal_coverage": "2025-12-22", "anyang_feature_count": 305, "schema_note": "file contains institution, road address, phone, managing department, 기준일자 only; no latitude/longitude columns"})
        elif record["id"].startswith("osm-"):
            record["temporal_coverage"] = "retrieval snapshot 2026-08-20"
        datasets.append(record)
    payload["datasets"] = datasets
    payload["required_source_ids"] = [
        "civil-defense-shelter-national", "earthquake-outdoor-shelter", "emergency-water-national-standard",
        "aed-anyang-file", "emergency-medical-institutions", "fire-water-standard", "emergency-alerts", "kma-weather",
        "flood-traces", "gis-buildings", "osm-anyang-pedestrian-broad", "sgis-population", "environment-land-cover", "dem-terrain",
    ]
    payload["status_rule"] = "Every required source has an evidence-backed status; no blocker is treated as a downloaded dataset."
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
