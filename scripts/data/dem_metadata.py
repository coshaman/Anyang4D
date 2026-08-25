from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


def parse_grid_interval_m(value: str | None) -> float | None:
    if not value:
        return None
    numbers = re.findall(r"\d+(?:\.\d+)?", value.replace(",", ""))
    if not numbers:
        return None
    return float(numbers[0])


def select_anyang_sheets(rows: Iterable[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in rows:
        sheet_name = (row.get("도엽명5000") or "").strip()
        if "안양" not in sheet_name:
            continue
        selected.append(
            {
                "sheet_number": (row.get("도엽번호5000") or "").strip(),
                "sheet_name": sheet_name,
                "grid_interval": (row.get("격자간격") or "").strip() or None,
                "grid_interval_m": parse_grid_interval_m(row.get("격자간격")),
                "production_year": (row.get("원시자료제작년도") or "").strip() or None,
                "data_format": (row.get("자료형식") or "").strip() or None,
                "crs": (row.get("좌표계") or "").strip() or None,
                "vertical_datum": (row.get("표고기준") or "").strip() or None,
                "source_data": (row.get("원시자료") or "").strip() or None,
                "acquisition_method": (row.get("원시자료획득방법") or "").strip() or None,
                "accuracy": (row.get("정확도") or "").strip() or None,
                "raw_lower_left_x": (row.get("원시좌하단의평면X좌표") or "").strip() or None,
                "raw_lower_left_y": (row.get("원시좌하단의평면Y좌표") or "").strip() or None,
                "raw_upper_right_x": (row.get("원시우상단의평면X좌표") or "").strip() or None,
                "raw_upper_right_y": (row.get("원시우상단의평면Y좌표") or "").strip() or None,
            }
        )
    return selected


def audit_dem_metadata(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="cp949", newline="") as handle:
        rows = list(csv.DictReader(handle))
    selected = select_anyang_sheets(rows)
    intervals = [record["grid_interval_m"] for record in selected if record["grid_interval_m"] is not None]
    return {
        "source": {
            "dataset_title": "국토교통부 국토지리정보원_항공사진_수치표고성과내역",
            "url": "https://www.data.go.kr/data/15067637/fileData.do",
            "local_path": path.as_posix(),
            "encoding": "cp949",
            "is_dem_raster": False,
        },
        "raw_row_count": len(rows),
        "anyang_record_count": len(selected),
        "anyang_sheet_count": len({record["sheet_number"] for record in selected}),
        "best_recorded_grid_interval_m": min(intervals) if intervals else None,
        "grid_interval_counts": dict(Counter(str(value) for value in intervals)),
        "sheet_records": selected,
        "raster_access": {
            "status": "HUMAN_AUTH_REQUIRED",
            "is_metadata_only": True,
            "dataset_title": "국토교통부 국토지리정보원_DEM_20240924",
            "url": "https://www.data.go.kr/data/15059920/fileData.do",
            "download_url": "http://map.ngii.go.kr/ms/map/NlipMap.do?tabGb=total",
            "reason": "국토정보플랫폼 공개DEM 다운로드는 로그인과 대용량 파일전송 도구가 필요함",
        },
    }
