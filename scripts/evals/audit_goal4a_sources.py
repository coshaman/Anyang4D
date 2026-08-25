from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/evals/data/goal4a-source-audit.json"


def main() -> None:
    facilities = json.loads((ROOT / "data/processed/anyang_facilities.json").read_text(encoding="utf-8"))["records"]
    counts = {}
    for record in facilities:
        counts[record["category"]] = counts.get(record["category"], 0) + 1
    sources = [
        {"id": "civil-defense-shelter-national", "status": "DOWNLOADED", "role": "evacuation eligibility and capacity", "count": counts.get("CIVIL_DEFENSE_SHELTER", 0), "provenance": "OFFICIAL"},
        {"id": "anyang-local-emergency-shelter", "status": "HUMAN_AUTH_REQUIRED", "role": "shelter crosswalk", "count": None, "provenance": "STALE_OR_UNKNOWN", "reason": "local 213-row file is not present"},
        {"id": "emergency-water-national-standard", "status": "DOWNLOADED", "role": "official response-resource context, not evacuation capacity", "count": counts.get("EMERGENCY_WATER", 0), "provenance": "OFFICIAL", "capacity_fields": "not present in source"},
        {"id": "anyang-local-emergency-water", "status": "HUMAN_AUTH_REQUIRED", "role": "water capacity crosswalk", "count": None, "provenance": "STALE_OR_UNKNOWN", "reason": "local 46-row file is not present"},
        {"id": "aed-anyang-file", "status": "DOWNLOADED", "role": "119 context only; not evacuation capacity", "count": counts.get("AED", 0), "provenance": "OFFICIAL", "coordinates": "missing in source"},
        {"id": "anyang-administrative-dong-population", "status": "DOWNLOADED", "role": "official demand units", "count": 31, "total_population": 562143, "provenance": "OFFICIAL", "source_period": "2026-07-31", "allocation_policy": "SIMULATED_SPATIAL_ALLOCATION_UNIFORM_DONG_ANCHOR; no dong polygons in source"},
        {"id": "earthquake-outdoor-shelter", "status": "HUMAN_AUTH_REQUIRED", "role": "earthquake eligibility", "count": None, "provenance": "STALE_OR_UNKNOWN"},
        {"id": "fire-water-facilities", "status": "HUMAN_AUTH_REQUIRED", "role": "fire context", "count": None, "provenance": "STALE_OR_UNKNOWN"},
        {"id": "drainage-pump-stations", "status": "NOT_YET_ATTEMPTED", "role": "official infrastructure context", "count": None, "provenance": "STALE_OR_UNKNOWN", "reason": "no login-free Anyang official file identified during Goal 4A acquisition"},
        {"id": "flood-response-material-inventory", "status": "NOT_YET_ATTEMPTED", "role": "admin resource layer", "count": None, "provenance": "STALE_OR_UNKNOWN", "reason": "no login-free Anyang official file identified during Goal 4A acquisition"},
        {"id": "osm-anyang-pedestrian-demo", "status": "DOWNLOADED", "role": "interactive scenario road graph", "count": None, "provenance": "OFFICIAL"},
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema_version": "0.1.0", "sources": sources, "population_policy": "Official 2026-07-31 dong totals are used as demand; coordinates are explicitly SIMULATED_SPATIAL_ALLOCATION anchors, not census-grid truth.", "terrain_policy": "TERRAIN_C remains diagnostic-only; no terrain-derived flood state is used."}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
