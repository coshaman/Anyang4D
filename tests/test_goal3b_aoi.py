import json

from scripts.data.select_demo_aoi import select_demo_aoi


def test_demo_aoi_is_bounded_and_has_minimum_1m_sheet_set(tmp_path):
    result = select_demo_aoi(output_path=tmp_path / "demo-aoi.geojson")
    geojson = json.loads((tmp_path / "demo-aoi.geojson").read_text(encoding="utf-8"))
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 1
    assert 0 < result["sheet_count"] <= 4
    assert all(record["grid_interval_m"] == 1.0 for record in result["sheets"])
    assert len({record["sheet_id"] for record in result["sheets"]}) == result["sheet_count"]
