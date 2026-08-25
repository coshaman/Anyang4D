from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    manifest = json.loads((ROOT / "data/manifests/data_manifest.json").read_text(encoding="utf-8"))
    boundary = manifest["goal4a_terrain_boundary"]
    facilities = json.loads((ROOT / "data/processed/anyang_facilities.json").read_text(encoding="utf-8"))["records"]
    local_shelters = json.loads((ROOT / "data/processed/anyang_local_shelters.json").read_text(encoding="utf-8"))
    resources = json.loads((ROOT / "data/processed/anyang_local_resources.json").read_text(encoding="utf-8"))
    crosswalk = json.loads((ROOT / "artifacts/evals/data/goal4b-shelter-crosswalk.json").read_text(encoding="utf-8"))
    checks = {
        "final_terrain_class": boundary["final_terrain_class"] == "TERRAIN_C",
        "street_level_flood_terrain_path": boundary["street_level_flood_terrain_path"] == "DROP",
        "terrain_derived_flood_disabled": boundary["terrain_derived_flood"] is False,
        "national_shelter_count": sum(item.get("category") == "CIVIL_DEFENSE_SHELTER" for item in facilities) == 231,
        "national_water_count": sum(item.get("category") == "EMERGENCY_WATER" for item in facilities) == 71,
        "local_shelter_count": local_shelters["record_count"] == 224,
        "local_water_count": resources["water"]["record_count"] == 46,
        "local_inventory_count": resources["flood_response_inventory"]["record_count"] == 33,
        "crosswalk_preserves_both_sources": crosswalk["local_count"] == 224 and crosswalk["national_count"] == 231,
        "national_explicit_provenance": all(item.get("source_provenance") == "NATIONAL_OFFICIAL_FILTERED_ANYANG" for item in facilities if item.get("category") != "AED"),
        "local_explicit_provenance": all(item.get("provenance") == "ANYANG_LOCAL_OFFICIAL" for item in local_shelters["items"]),
    }
    artifact = {"checks": checks, "all_pass": all(checks.values()), "policy": {"terrain": "TERRAIN_C", "street_level_flood": "DROP", "citizen_routing_from_terrain": "DROP", "ai": "DROP"}}
    output = ROOT / "artifacts/evals/data/goal4b-boundary-audit.json"
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, ensure_ascii=False))
    if not artifact["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
