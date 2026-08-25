from __future__ import annotations

import json
from pathlib import Path

from services.api.main import facilities, foundation
from services.api.goal4a import resource_inventory, resources


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/evals/release/data-consistency.json"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> int:
    manifest = load("data/manifests/data_manifest.json")
    datasets = {item["id"]: item for item in manifest["datasets"]}
    processed_facilities = load("data/processed/anyang_facilities.json")["records"]
    local_shelters = load("data/processed/anyang_local_shelters.json")
    local_resources = load("data/processed/anyang_local_resources.json")
    population = load("data/processed/anyang_population.json")
    api_foundation = foundation().model_dump()
    api_shelters = facilities("civil_defense").model_dump()
    api_water = facilities("water").model_dump()
    api_aed = facilities("aed").model_dump()
    api_resources = resources()
    api_inventory = resource_inventory()

    counts = {
        "local_shelters": local_shelters["record_count"],
        "national_filtered_shelters": sum(item["category"] == "CIVIL_DEFENSE_SHELTER" for item in processed_facilities),
        "national_filtered_water": sum(item["category"] == "EMERGENCY_WATER" for item in processed_facilities),
        "aeds": sum(item["category"] == "AED" for item in processed_facilities),
        "local_water": local_resources["water"]["record_count"],
        "response_inventory": local_resources["flood_response_inventory"]["record_count"],
        "population_units": len(population["units"]),
        "population_total": population["total_population"],
    }
    checks = {
        "processed_counts_match_manifest": counts["national_filtered_shelters"] == datasets["civil-defense-shelter-national"]["anyang_feature_count"] and counts["national_filtered_water"] == datasets["emergency-water-national-standard"]["anyang_feature_count"] and counts["aeds"] == datasets["aed-anyang-file"]["anyang_feature_count"],
        "api_foundation_matches_processed": api_foundation["counts"] == {"CIVIL_DEFENSE_SHELTER": counts["national_filtered_shelters"], "EMERGENCY_WATER": counts["national_filtered_water"], "AED": counts["aeds"]},
        "api_facility_lists_match_processed": len(api_shelters["items"]) == counts["national_filtered_shelters"] and len(api_water["items"]) == counts["national_filtered_water"] and len(api_aed["items"]) == counts["aeds"],
        "api_local_context_matches_processed": api_resources["count"] == counts["local_water"] + counts["national_filtered_water"] and api_inventory["count"] == counts["response_inventory"],
        "population_matches_processed": counts["population_units"] == 31 and counts["population_total"] == 562143,
        "source_hashes_present": all(datasets[key].get("sha256") for key in ("civil-defense-shelter-national", "emergency-water-national-standard", "aed-anyang-file", "anyang-administrative-dong-population")),
        "source_dates_present": all(datasets[key].get("retrieved_at") or datasets[key].get("retrieval_timestamp") for key in ("civil-defense-shelter-national", "emergency-water-national-standard", "aed-anyang-file", "anyang-administrative-dong-population")),
    }
    payload = {"schema_version": "goal6a-release-data-consistency-v1", "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "counts": counts, "sources": {key: {"status": datasets[key].get("status"), "temporal_coverage": datasets[key].get("temporal_coverage"), "retrieved_at": datasets[key].get("retrieved_at") or datasets[key].get("retrieval_timestamp"), "sha256": datasets[key].get("sha256"), "license_terms": datasets[key].get("license_terms")} for key in ("civil-defense-shelter-national", "emergency-water-national-standard", "aed-anyang-file", "anyang-administrative-dong-population", "osm-anyang-pedestrian-demo")}, "provenance": {"national": "NATIONAL_OFFICIAL_FILTERED_ANYANG", "local": "ANYANG_LOCAL_OFFICIAL", "population": population["population_basis"], "population_allocation": population["allocation_policy"]}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
