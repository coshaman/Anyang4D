from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.data.dem_metadata import audit_dem_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit NGII DEM metadata and Anyang sheets")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_dem_metadata(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("raw_row_count", "anyang_record_count", "anyang_sheet_count", "best_recorded_grid_interval_m")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
