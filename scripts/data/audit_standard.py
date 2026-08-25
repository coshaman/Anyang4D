from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def audit_json(path: Path, *, region_terms: tuple[str, ...] = ("안양", "Anyang")) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    fields = payload.get("fields", [])
    rows = [row for row in records if any(term in json.dumps(row, ensure_ascii=False) for term in region_terms)]
    return {
        "raw_record_count": len(records),
        "anyang_record_count": len(rows),
        "field_count": len(fields),
        "field_names": [field.get("id") for field in fields],
        "sample_records": rows[:3],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit_json(args.path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
