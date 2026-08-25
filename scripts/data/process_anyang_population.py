"""Normalize the current official Anyang dong population workbook.

The workbook contains official totals but no dong polygons. Coordinates in the
processed output are therefore explicit simulation anchors, not census-grid
centroids. The solver uses the official population totals and preserves this
allocation caveat in every demand unit.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/raw/anyang_population/anyang_resident_population_202607.xlsx"
OUTPUT = ROOT / "data/processed/anyang_population.json"
SOURCE_URL = "https://www.anyang.go.kr/main/selectAyPopulaion.do?bbsNo=56&integrDeptCode=&key=&nttNo=453089&pageIndex=1&searchCnd=all&searchCtgry=&searchKrwd=2026"


def _number(value: Any) -> int:
    return int(str(value).replace(",", "").strip())


def _anchors(count: int) -> list[tuple[float, float]]:
    # Anyang AOI anchors used only to make dong totals routable in the bounded
    # demo graph. They are not administrative centroids or a population grid.
    west, east, south, north = 126.895, 126.995, 37.355, 37.435
    cols = 6
    return [(south + (north - south) * (index // cols + 0.5) / ((count + cols - 1) // cols),
             west + (east - west) * (index % cols + 0.5) / cols) for index in range(count)]


def main() -> None:
    workbook = openpyxl.load_workbook(SOURCE, data_only=True, read_only=True)
    rows = []
    for row in workbook.worksheets[0].iter_rows(min_row=7, max_col=3, values_only=True):
        name, households, population = row
        if isinstance(name, str) and name.endswith("동"):
            rows.append({"dong_name": name, "population": _number(population)})
    if len(rows) != 31 or sum(item["population"] for item in rows) != 562143:
        raise ValueError(f"unexpected Anyang dong population rows: count={len(rows)} total={sum(item['population'] for item in rows)}")
    anchors = _anchors(len(rows))
    units = []
    for index, (item, (latitude, longitude)) in enumerate(zip(rows, anchors, strict=True)):
        units.append({
            "demand_id": f"anyang-dong-{index + 1:02d}",
            "label": item["dong_name"],
            "dong_name": item["dong_name"],
            "dong_code": None,
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "population": item["population"],
            "provenance": "OFFICIAL",
            "source_period": "2026-07-31",
            "allocation_method": "SIMULATED_SPATIAL_ALLOCATION_UNIFORM_DONG_ANCHOR",
            "allocation_provenance": "SIMULATED",
        })
    payload = {
        "schema_version": "1.0.0",
        "source": {"provider": "안양시", "title": "2026년 7월말 기준 주민등록 인구현황", "source_period": "2026-07-31", "url": SOURCE_URL, "raw_path": str(SOURCE.relative_to(ROOT)), "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
        "population_basis": "official registered resident population, foreign residents excluded",
        "allocation_policy": "Official dong totals are preserved exactly. Coordinates are bounded demo anchors because the source has no dong polygons; they are not census-grid truth.",
        "total_population": sum(item["population"] for item in units),
        "units": units,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "units": len(units), "total_population": payload["total_population"], "sha256": payload["source"]["sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
