from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/evals/data/goal4a-facility-filter-audit.json"


def count(path: Path, fields: tuple[str, ...]) -> dict[str, int]:
    rows = list(csv.DictReader(path.open("r", encoding="cp949", newline="")))
    broad = sum("안양" in " ".join(str(value or "") for value in row.values()) for row in rows)
    strict = sum("안양시" in " ".join(str(row.get(field) or "") for field in fields) for row in rows)
    return {"raw_rows": len(rows), "broad_substring_rows": broad, "strict_anyangsi_rows": strict}


def main() -> None:
    payload = {
        "shelter": count(ROOT / "data/raw/localdata/civil_defense_shelter/source.csv", ("소재지전체주소", "도로명전체주소", "지번주소")),
        "emergency_water": count(ROOT / "data/raw/localdata/emergency_water/source.csv", ("도로명주소", "지번주소")),
        "rule": "Operational facility records require 안양시 in the relevant address fields; substring-only matches such as 안양천 are excluded.",
        "processed_counts": {"CIVIL_DEFENSE_SHELTER": 231, "EMERGENCY_WATER": 71},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
