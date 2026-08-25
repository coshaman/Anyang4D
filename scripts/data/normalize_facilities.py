from __future__ import annotations

import json
from pathlib import Path

from services.api.facilities import load_real_facilities


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    output = ROOT / "data/processed/anyang_facilities.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    records = load_real_facilities()
    output.write_text(json.dumps({"schema_version": "1.0.0", "generated_from": "data/manifests/data_manifest.json", "records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for record in records:
        counts[record["category"]] = counts.get(record["category"], 0) + 1
    print(json.dumps({"output": output.as_posix(), "counts": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
