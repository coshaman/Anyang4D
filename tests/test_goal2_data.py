import pytest

from services.api.facilities import load_real_facilities, normalize_aed_row, normalize_shelter_row, normalize_water_row
from services.api.routing import build_route


def test_shelter_normalization_preserves_source_missingness():
    row = {
        "관리번호": "S-1",
        "시설명": "안양 대피시설",
        "시설구분": "민방위",
        "시설위치(지상/지하)": "지하",
        "시설면적(㎡)": "100",
        "최대수용인원": "",
        "위도(EPSG4326)": "37.4",
        "경도(EPSG4326)": "126.9",
        "도로명전체주소": "안양시 예시로 1",
        "운영상태": "",
        "데이터갱신시점": "2026-02-01 10:00:00",
    }

    item = normalize_shelter_row(row)

    assert item["provenance"] == "OFFICIAL"
    assert item["capacity"] is None
    assert item["operating_info"] is None
    assert item["latitude"] == pytest.approx(37.4)
    assert item["source_dataset_id"] == "civil-defense-shelter-national"
    assert item["data_quality_flags"]


def test_water_normalization_keeps_projected_source_crs_and_converts_coordinates():
    row = {
        "관리번호": "W-1",
        "시설명건물명": "안양 급수시설",
        "시설구분명": "민방위급수시설",
        "좌표정보(X)": "189878.40729119",
        "좌표정보(Y)": "448255.199632516",
        "도로명주소": "안양시 예시로 2",
        "최종수정시점": "2026-04-01 10:00:00",
    }

    item = normalize_water_row(row)

    assert item["source_crs"] == "EPSG:5174"
    assert item["latitude"] == pytest.approx(37.5365, abs=0.002)
    assert item["longitude"] == pytest.approx(126.8879, abs=0.002)
    assert item["capacity"] is None


def test_aed_normalization_does_not_invent_coordinates_or_access():
    item = normalize_aed_row({
        "설치기관명": "안양 AED",
        "소재지도로명주소": "안양시 예시로 3",
        "전화번호": "031-000-0000",
        "데이터기준일자": "2025-12-22",
    })

    assert item["latitude"] is None
    assert item["longitude"] is None
    assert item["access_info"] is None
    assert "NO_COORDINATES_IN_SOURCE" in item["data_quality_flags"]


def test_route_returns_geometry_distance_and_no_hazard_metadata():
    payload = {
        "elements": [
            {"type": "node", "id": 1, "lat": 37.4, "lon": 126.9},
            {"type": "node", "id": 2, "lat": 37.401, "lon": 126.901},
            {"type": "node", "id": 3, "lat": 37.402, "lon": 126.902},
            {"type": "way", "id": 10, "nodes": [1, 2, 3], "tags": {"highway": "footway"}},
        ]
    }

    route = build_route(payload, (37.4, 126.9), (37.402, 126.902))

    assert route["distance_m"] > 0
    assert route["estimated_walking_minutes"] > 0
    assert len(route["geometry"]) == 3
    assert route["hazard_exposure"] is None
    assert route["provenance"] == "OFFICIAL"


def test_route_reports_disconnected_graph_without_fabricating_path():
    payload = {
        "elements": [
            {"type": "node", "id": 1, "lat": 37.4, "lon": 126.9},
            {"type": "node", "id": 2, "lat": 37.5, "lon": 127.0},
            {"type": "way", "id": 10, "nodes": [1], "tags": {"highway": "footway"}},
            {"type": "way", "id": 11, "nodes": [2], "tags": {"highway": "footway"}},
        ]
    }

    with pytest.raises(ValueError, match="no pedestrian path"):
        build_route(payload, (37.4, 126.9), (37.5, 127.0))


def test_real_facility_loader_reproduces_goal1_counts():
    records = load_real_facilities()
    counts = {}
    for record in records:
        counts[record["category"]] = counts.get(record["category"], 0) + 1

    assert counts == {"CIVIL_DEFENSE_SHELTER": 231, "EMERGENCY_WATER": 71, "AED": 305}
    assert all(record["provenance"] == "OFFICIAL" for record in records)
