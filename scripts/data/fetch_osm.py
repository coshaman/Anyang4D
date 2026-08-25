from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests

from .audit_sources import SourceStatus
from .fetch_sources import ROOT, load_manifest, save_manifest, sha256_file, utc_now, upsert_record


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def query_overpass(south: float, west: float, north: float, east: float) -> dict:
    query = f"[out:json][timeout:180];(way[highway]({south},{west},{north},{east});>;);out body;"
    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers={"User-Agent": "SAFE-Twin-Anyang-data-audit/0.1"},
        timeout=240,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--raw-path", required=True)
    parser.add_argument("--south", type=float, required=True)
    parser.add_argument("--west", type=float, required=True)
    parser.add_argument("--north", type=float, required=True)
    parser.add_argument("--east", type=float, required=True)
    args = parser.parse_args()
    destination = ROOT / args.raw_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "id": args.id,
        "dataset_title": args.title,
        "provider": "OpenStreetMap / Overpass API",
        "landing_url": "https://www.openstreetmap.org/copyright",
        "actual_download_url": OVERPASS_URL,
        "license_terms": "ODbL 1.0; attribution required",
        "auth_requirement": "none observed",
        "retrieval_timestamp": utc_now(),
        "crs": "EPSG:4326",
        "temporal_coverage": "retrieval snapshot",
        "anyang_feature_count": None,
        "preprocessing_script": "scripts/data/audit_osm.py",
        "status": SourceStatus.FAILED.value,
        "bbox": [args.south, args.west, args.north, args.east],
    }
    try:
        payload = query_overpass(args.south, args.west, args.north, args.east)
        destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        record.update({
            "status": SourceStatus.DOWNLOADED.value,
            "local_path": destination.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(destination),
            "bytes": destination.stat().st_size,
            "osm_element_count": len(payload.get("elements", [])),
        })
    except (requests.RequestException, ValueError) as exc:
        record["error"] = str(exc)
    manifest = load_manifest()
    upsert_record(manifest, record)
    save_manifest(manifest)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
