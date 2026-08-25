from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def distance_m(a: tuple[float, float] | None, b: tuple[float, float] | None) -> float | None:
    if not a or not b:
        return None
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6_371_000 * 2 * math.asin(math.sqrt(h))


facilities = json.loads((ROOT / "data/processed/anyang_facilities.json").read_text(encoding="utf-8"))["records"]
national_shelters = [item for item in facilities if item.get("category") == "CIVIL_DEFENSE_SHELTER"]
local = json.loads((ROOT / "data/processed/anyang_local_shelters.json").read_text(encoding="utf-8"))["items"]
matches: list[dict] = []
used_national: set[str] = set()
for local_item in local:
    lp = (local_item.get("latitude"), local_item.get("longitude"))
    candidates = []
    for item in national_shelters:
        if item["id"] in used_national:
            continue
        distance = distance_m(lp, (item.get("latitude"), item.get("longitude")))
        if distance is not None:
            candidates.append((distance, item))
    candidates.sort(key=lambda pair: pair[0])
    best = candidates[0] if candidates else (None, None)
    if best[0] is not None and best[0] <= 100:
        used_national.add(best[1]["id"])
        classification = "EXACT_MATCH" if best[0] <= 10 else "STRONG_MATCH"
        matches.append({"classification": classification, "distance_m": round(best[0], 2), "local": local_item, "national": best[1], "chosen_operational_value": "PRESERVE_BOTH_SOURCES_UNMERGED"})
    else:
        matches.append({"classification": "LOCAL_ONLY", "distance_m": None, "local": local_item, "national": None, "chosen_operational_value": "LOCAL_RECORD_ONLY"})
for item in national_shelters:
    if item["id"] not in used_national:
        matches.append({"classification": "NATIONAL_ONLY", "distance_m": None, "local": None, "national": item, "chosen_operational_value": "NATIONAL_RECORD_ONLY"})

classes = ["EXACT_MATCH", "STRONG_MATCH", "AMBIGUOUS", "LOCAL_ONLY", "NATIONAL_ONLY"]
counts = {key: sum(1 for item in matches if item["classification"] == key) for key in classes}
out = {
    "schema_version": "0.1.0",
    "match_method": "coordinate-nearest with 100m conservative threshold; source names and addresses retained for review",
    "local_count": len(local),
    "national_count": len(national_shelters),
    "counts": counts,
    "matches": matches,
    "provenance": "ANYANG_LOCAL_OFFICIAL vs NATIONAL_OFFICIAL_FILTERED_ANYANG",
}
path = ROOT / "artifacts/evals/data/goal4b-shelter-crosswalk.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"local_count": len(local), "national_count": len(national_shelters), "counts": counts}, ensure_ascii=False))

resource_payload = json.loads((ROOT / "data/processed/anyang_local_resources.json").read_text(encoding="utf-8"))
local_water = resource_payload["water"]["normalized_items"]
national_water = [item for item in facilities if item.get("category") == "EMERGENCY_WATER"]
water_matches = []
used_water: set[str] = set()
for local_item in local_water:
    local_text = re.sub(r"[^0-9a-z가-힣]", "", f"{local_item.get('name', '')}{local_item.get('address', '')}".lower())
    candidates = []
    for item in national_water:
        national_text = re.sub(r"[^0-9a-z가-힣]", "", f"{item.get('name', '')}{item.get('address', '')}".lower())
        score = 2 if local_item.get("name") and local_item["name"] in str(item.get("name")) else 0
        if local_text and national_text and (local_text in national_text or national_text in local_text):
            score += 1
        if score:
            candidates.append((score, item))
    candidates.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    if candidates and candidates[0][0] >= 2 and candidates[0][1]["id"] not in used_water:
        match = candidates[0][1]
        used_water.add(match["id"])
        water_matches.append({"classification": "STRONG_MATCH", "local": local_item, "national": match, "capacity_fields": {"local_capacity_tons_per_day": local_item["capacity_tons_per_day"], "local_available_persons": local_item["available_persons"], "national_capacity": match.get("capacity")}, "chosen_operational_value": "PRESERVE_LOCAL_RESPONSE_CAPACITY"})
    else:
        water_matches.append({"classification": "LOCAL_ONLY", "local": local_item, "national": None, "capacity_fields": {"local_capacity_tons_per_day": local_item["capacity_tons_per_day"], "local_available_persons": local_item["available_persons"]}, "chosen_operational_value": "LOCAL_RESPONSE_RESOURCE_ONLY"})
for item in national_water:
    if item["id"] not in used_water:
        water_matches.append({"classification": "NATIONAL_ONLY", "local": None, "national": item, "capacity_fields": {"national_capacity": item.get("capacity")}, "chosen_operational_value": "NATIONAL_CONTEXT_ONLY"})
water_out = {"schema_version": "0.1.0", "local_count": len(local_water), "national_count": len(national_water), "counts": {key: sum(1 for item in water_matches if item["classification"] == key) for key in ["EXACT_MATCH", "STRONG_MATCH", "AMBIGUOUS", "LOCAL_ONLY", "NATIONAL_ONLY"]}, "matches": water_matches, "capacity_policy": "Only local official fields are used as RESPONSE_RESOURCE_CAPACITY; never as evacuation shelter capacity.", "provenance": "ANYANG_LOCAL_OFFICIAL vs NATIONAL_OFFICIAL_FILTERED_ANYANG"}
(ROOT / "artifacts/evals/data/goal4b-water-crosswalk.json").write_text(json.dumps(water_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
