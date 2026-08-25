from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/goal4b"
OUT = ROOT / "data/processed/anyang_local_resources.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="cp949", newline="") as handle:
        return list(csv.DictReader(handle))


water = read_csv(RAW / "water.csv")
inventory = read_csv(RAW / "inventory.csv")
water_normalized = [{
    "resource_id": f"anyang-local-emergency-water:{row.get('연번', index + 1)}",
    "name": row.get("시설명", "").strip(),
    "address": row.get("주소", "").strip(),
    "use": row.get("용도", "").strip(),
    "capacity_tons_per_day": float(row.get("급수용량(톤_일)", "0").strip() or 0),
    "available_persons": int(float(row.get(" 사용가능인원 ", "0").strip() or 0)),
    "capacity_role": "RESPONSE_RESOURCE_CAPACITY",
    "provenance": "ANYANG_LOCAL_OFFICIAL",
} for index, row in enumerate(water)]
inventory_normalized = [{
    "location": row.get("구분", "").strip(),
    "items": {key: row[key].strip() for key in row if key != "구분"},
    "provenance": "ANYANG_LOCAL_OFFICIAL",
} for row in inventory]
payload = {
    "schema_version": "0.1.0",
    "provider": "경기도 안양시",
    "retrieved_at": datetime.now(timezone.utc).isoformat(),
    "water": {
        "dataset_title": "민방위 급수시설 현황",
        "source_url": "https://www.data.go.kr/data/3045178/fileData.do?recommendDataYn=Y",
        "source_period": "2025-03-12",
        "source_file": {"path": "data/raw/goal4b/water.csv", "sha256": hashlib.sha256((RAW / "water.csv").read_bytes()).hexdigest()},
        "record_count": len(water),
        "columns": list(water[0]) if water else [],
        "items": water,
        "normalized_items": water_normalized,
        "provenance": "ANYANG_LOCAL_OFFICIAL",
        "capacity_fields_verified": ["급수용량(톤/일)", "사용가능인원(명)"],
    },
    "flood_response_inventory": {
        "dataset_title": "수방자재 현황",
        "source_url": "https://www.data.go.kr/data/15085817/fileData.do?recommendDataYn=Y",
        "source_period": "2025-12-30",
        "source_file": {"path": "data/raw/goal4b/inventory.csv", "sha256": hashlib.sha256((RAW / "inventory.csv").read_bytes()).hexdigest()},
        "record_count": len(inventory),
        "columns": list(inventory[0]) if inventory else [],
        "items": inventory,
        "normalized_items": inventory_normalized,
        "provenance": "ANYANG_LOCAL_OFFICIAL",
        "notes": ["재난 대응자원 맥락으로만 사용", "자동 dispatch나 필요량 추정에 사용하지 않음"],
    },
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"water": len(water), "inventory": len(inventory), "water_columns": list(water[0]) if water else [], "inventory_columns": list(inventory[0]) if inventory else []}, ensure_ascii=False))
