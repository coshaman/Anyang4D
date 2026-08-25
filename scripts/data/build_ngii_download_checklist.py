from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "data/raw/ngii/dem_metadata_20231107.csv"
JSON_PATH = ROOT / "artifacts/evals/data/ngii-target-1m-records.json"
MD_PATH = ROOT / "docs/NGII_1M_EXACT_DOWNLOAD_CHECKLIST.md"
TARGETS = ["안양048", "안양049", "안양058", "안양059"]


def clean(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def project_coordinates(row: dict[str, str]) -> dict[str, str | None]:
    # The 1 m rows store the footprint in the 원시좌하단/원시우상단 fields.
    pairs = {
        "lower_left_x": ("원시좌하단의평면X좌표", "좌하단의평면X좌표"),
        "lower_left_y": ("원시좌하단의평면Y좌표", "좌하단의평면Y좌표"),
        "upper_right_x": ("원시우상단의평면X좌표", "우상단의평면X좌표"),
        "upper_right_y": ("원시우상단의평면Y좌표", "우상단의평면Y좌표"),
    }
    return {key: clean(row[first]) or clean(row[second]) for key, (first, second) in pairs.items()}


def normalize(row: dict[str, str]) -> dict[str, object]:
    coords = project_coordinates(row)
    return {
        "도엽명5000": clean(row["도엽명5000"]),
        "도엽번호5000": clean(row["도엽번호5000"]),
        "구축구분코드": clean(row["구축구분코드"]),
        "자료명칭": clean(row["자료명칭"]),
        "자료형식": clean(row["자료형식"]),
        "격자간격": clean(row["격자간격"]),
        "격자간격_m": 1.0 if "1m" in row["격자간격"].replace(" ", "").lower() else (10.0 if "10m" in row["격자간격"].replace(" ", "").lower() else None),
        "제작년도": clean(row["원시자료제작년도"]),
        "원시자료": clean(row["원시자료"]),
        "원시자료획득방법": clean(row["원시자료획득방법"]),
        "지리좌표계": clean(row["지리좌표계"]),
        "좌표계": clean(row["좌표계"]),
        "원점구분": clean(row["원점구분"]),
        "표고기준": clean(row["표고기준"]),
        "정확도": clean(row["정확도"]),
        "lower_left": {"x": coords["lower_left_x"], "y": coords["lower_left_y"]},
        "upper_right": {"x": coords["upper_right_x"], "y": coords["upper_right_y"]},
        "자료기록형식": clean(row["자료기록형식"]),
        "보간방법": clean(row["보간방법"]),
        "높이값종류": clean(row["높이값종류"]),
        "최고표고": clean(row["최고표고"]),
        "최저표고": clean(row["최저표고"]),
    }


def sort_key(record: dict[str, object]) -> tuple[int, int, int, int, int]:
    interval = float(record["격자간격_m"] or 999)
    year = int(record["제작년도"] or 0)
    complete = sum(record.get(key) is not None for key in ("자료형식", "지리좌표계", "표고기준", "정확도"))
    explicit_crs = int(bool(record.get("좌표계") or record.get("지리좌표계")))
    explicit_vertical = int(bool(record.get("표고기준")))
    return (int(interval), -complete, -year, -explicit_crs, -explicit_vertical)


def main() -> None:
    with CSV_PATH.open(encoding="cp949", newline="") as handle:
        rows = list(csv.DictReader(handle))

    matches: dict[str, list[dict[str, object]]] = {target: [] for target in TARGETS}
    for row in rows:
        if row.get("도엽명5000") in matches:
            matches[row["도엽명5000"]].append(normalize(row))

    selected = {}
    ranked_1m = {}
    post_2020 = {}
    for target, records in matches.items():
        one_m = [record for record in records if record["격자간격_m"] == 1.0]
        ranked = sorted(one_m, key=sort_key)
        ranked_1m[target] = [
            {
                "rank": index,
                "record": record,
                "selection_reason": (
                    "preferred: complete relevant metadata, newer 2009 production year, explicit CRS and vertical datum, 0.25 m accuracy"
                    if index == 1 and record["제작년도"] == "2009"
                    else "older 1 m alternative: 2006 production, 세계측지계, 0.27 m accuracy"
                ),
            }
            for index, record in enumerate(ranked, start=1)
        ]
        selected[target] = ranked[0] if ranked else None
        post_2020[target] = [record for record in records if (record["제작년도"] and int(record["제작년도"]) >= 2020)]

    payload = {
        "schema_version": "0.1.0",
        "source_metadata": "data/raw/ngii/dem_metadata_20231107.csv",
        "source_encoding": "cp949",
        "official_ngii_download_page": "https://map.ngii.go.kr/ms/map/NlipMap.do?tabGb=total",
        "targets": TARGETS,
        "all_matching_metadata_records": matches,
        "best_historical_1m_record_per_sheet": selected,
        "ranked_1m_records_per_sheet": ranked_1m,
        "post_2020_records_per_sheet": post_2020,
        "all_four_have_post_2020_record_in_snapshot": all(bool(value) for value in post_2020.values()),
        "minimum_requested_production_year": 2020,
        "all_four_have_official_1m_record": all(value is not None for value in selected.values()),
        "ranking_rule": ["complete metadata", "newer production year", "explicit CRS", "explicit vertical datum", "accuracy"],
        "rejected_downloaded_product": {
            "sha256": "40873ee25879aa52ee6665f534f0083d3ab7ca1c21bbaf5ad7aa7f3dff954598",
            "driver": "HFA",
            "dimensions": [254, 316],
            "native_resolution_m": 90,
            "crs": "EPSG:5179",
            "nodata": -9999,
            "assessment": "wrong product; cannot be mapped to any target 1 m metadata record",
            "identification": "The exact catalog product cannot be identified from this metadata CSV. It resembles a regional 90 m product by spacing, but the target-sheet 90 m metadata records are PDF products and none matches the supplied IMG extent/format.",
        },
    }
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# NGII 1 m exact download checklist — SAFE-Twin Anyang",
        "",
        "Source metadata: `data/raw/ngii/dem_metadata_20231107.csv` (official NGII metadata snapshot; metadata only).",
        "",
        "Official NGII web UI: https://map.ngii.go.kr/ms/map/NlipMap.do?tabGb=total",
        "",
        "## Exact records to select",
        "",
        "IMPORTANT: the local official metadata snapshot contains no 2020-or-newer record for any of the four target sheets. The 2009 records below are historical 1 m reference records only and do **not** satisfy the requested minimum year. Do not download them if the 2020+ requirement is mandatory.",
        "",
        "The official NGII DEM dataset page is registered as a 2024 dataset and was modified in 2025, but the available per-sheet metadata CSV has no 2020+ production rows. The NGII UI must therefore be checked for a newer product directly.",
        "",
    ]
    for target in TARGETS:
        record = selected[target]
        lines.extend([
            f"### {target} / {record['도엽번호5000']} — historical 1 m reference, **not 2020+ compliant**",
            "",
            f"- Grid interval: **exactly 1 m × 1 m** (`{record['격자간격']}`)",
            f"- Production year: **{record['제작년도']}**",
            f"- Data/product name: **{record['자료명칭']}**",
            f"- Format expected: **{record['자료형식']}** (ASCII)",
            f"- CRS fields: **{record['좌표계']}**, 지리좌표계 code `{record['지리좌표계']}`, origin `{record['원점구분']}`",
            f"- Vertical datum: **{record['표고기준']}**",
            f"- Accuracy: **{record['정확도']}**",
            f"- Source/acquisition: `{record['원시자료']}` / `{record['원시자료획득방법']}`",
            f"- Lower-left: `(X={record['lower_left']['x']}, Y={record['lower_left']['y']})`",
            f"- Upper-right: `(X={record['upper_right']['x']}, Y={record['upper_right']['y']})`",
            "- UI distinguishing fields: `1m X 1m`, `2009`, `ASCII`, `평면직각좌표계`, `중부`, `인천항의 평균해수면`, `0.25 m`.",
            "",
        ])

    lines.extend([
        "## 2020+ selection rule for the NGII UI",
        "",
        "For each of the four sheet numbers above, select a record whose UI production/build year is **2020 or newer**, while retaining the following as cross-checks: native `1m X 1m`, `ASCII`, the sheet number, sheet-specific extent, explicit CRS, explicit vertical datum, and accuracy. If the UI shows only the 2009/2006 records documented here, stop; that is a HUMAN_ACTION_REQUIRED condition, not a successful 2020+ acquisition.",
        "",
    ])

    lines.extend([
        "## Reject the wrong product immediately",
        "",
        "After each download, do not assume success from the filename. Inspect the raster before adding it to `data/raw/ngii/` and reject it if:",
        "",
        "- X/Y pixel spacing is not approximately 1 m;",
        "- all four files have identical SHA-256;",
        "- raster dimensions/extents indicate one regional 90 m product;",
        "- CRS or extent does not match that sheet.",
        "",
        "The previously supplied files fail this test: all four have SHA-256 `40873ee25879aa52ee6665f534f0083d3ab7ca1c21bbaf5ad7aa7f3dff954598`, native 90 m spacing, and identical `254×316` EPSG:5179 HFA content. The exact catalog product cannot be identified from the local metadata CSV; it is not one of the target 1 m records.",
        "",
        "## HUMAN_ACTION_REQUIRED",
        "",
        f"Open the official NGII download page: https://map.ngii.go.kr/ms/map/NlipMap.do?tabGb=total",
        "",
        "Download exactly one native 1 m ASCII product for each target sheet only after the UI exposes a production/build year of 2020 or newer, preserving the NGII-provided filename and any sidecar metadata. If no 2020+ record is exposed, do not substitute the 2009/2006 record. Do not download a 10 m or 90 m record for Goal 3C. Login and the NGII large-file transfer workflow may be required.",
        "",
        "Evidence JSON: `artifacts/evals/data/ngii-target-1m-records.json`.",
    ])
    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
