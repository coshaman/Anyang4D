from pathlib import Path

import pytest

from scripts.data.dem_metadata import audit_dem_metadata, parse_grid_interval_m, select_anyang_sheets


def test_parse_grid_interval_handles_provider_variants() -> None:
    assert parse_grid_interval_m("1mX1m") == 1.0
    assert parse_grid_interval_m("1m x 1m") == 1.0
    assert parse_grid_interval_m("10 m") == 10.0
    assert parse_grid_interval_m("90mX90m") == 90.0


def test_select_anyang_sheets_uses_sheet_name_and_returns_summary() -> None:
    rows = [
        {"도엽번호5000": "37612001", "도엽명5000": "안양001", "격자간격": "1m x 1m", "원시자료제작년도": "2009"},
        {"도엽번호5000": "37612001", "도엽명5000": "안양001", "격자간격": "10 m", "원시자료제작년도": "2001"},
        {"도엽번호5000": "37703099", "도엽명5000": "춘천099", "격자간격": "1m x 1m", "원시자료제작년도": "2004"},
    ]
    selected = select_anyang_sheets(rows)
    assert len(selected) == 2
    assert {row["sheet_name"] for row in selected} == {"안양001"}
    assert {row["grid_interval_m"] for row in selected} == {1.0, 10.0}


def test_audit_dem_metadata_reports_real_file_and_access_gate() -> None:
    path = Path("data/raw/ngii/dem_metadata_20231107.csv")
    if not path.exists():
        pytest.skip("official metadata file is not present")
    report = audit_dem_metadata(path)
    assert report["raw_row_count"] == 23190
    assert report["anyang_record_count"] == 359
    assert report["anyang_sheet_count"] >= 100
    assert report["best_recorded_grid_interval_m"] == 1.0
    assert report["raster_access"]["status"] == "HUMAN_AUTH_REQUIRED"
    assert report["raster_access"]["is_metadata_only"] is True


def test_audit_preserves_vertical_datum_and_production_year() -> None:
    report = audit_dem_metadata(Path("data/raw/ngii/dem_metadata_20231107.csv"))
    one_m = [record for record in report["sheet_records"] if record["grid_interval_m"] == 1.0]
    assert {record["production_year"] for record in one_m} == {"2006", "2007", "2009"}
    assert {record["vertical_datum"] for record in one_m} == {"인천항의 평균해수면"}
