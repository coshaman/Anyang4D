from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from pyproj import Transformer


ROOT = Path(__file__).resolve().parents[2]
WATER_TO_WGS84 = Transformer.from_crs("EPSG:5174", "EPSG:4326", always_xy=True)


def _text(row: dict[str, Any], *names: str) -> str | None:
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _number(row: dict[str, Any], *names: str) -> float | int | None:
    value = _text(row, *names)
    if value is None:
        return None
    try:
        number = float(value.replace(",", ""))
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def _coordinate(row: dict[str, Any], lat_name: str, lon_name: str) -> tuple[float | None, float | None]:
    lat = _number(row, lat_name)
    lon = _number(row, lon_name)
    if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None, None
    return float(lat), float(lon)


def _stable_id(dataset_id: str, row: dict[str, Any], *identity_fields: str) -> str:
    identity = "|".join(_text(row, field) or "" for field in identity_fields)
    if not identity.strip():
        identity = "|".join(str(value or "") for value in row.values())
    digest = hashlib.sha256(f"{dataset_id}|{identity}".encode("utf-8")).hexdigest()[:16]
    return f"{dataset_id}:{digest}"


def _base(dataset_id: str, row: dict[str, Any], category: str, provider: str, source_crs: str | None, *identity_fields: str) -> dict[str, Any]:
    source_provenance = "NATIONAL_OFFICIAL_FILTERED_ANYANG" if dataset_id in {"civil-defense-shelter-national", "emergency-water-national-standard"} else "ANYANG_LOCAL_OFFICIAL"
    return {
        "id": _stable_id(dataset_id, row, *identity_fields),
        "source_dataset_id": dataset_id,
        "name": None,
        "category": category,
        "latitude": None,
        "longitude": None,
        "source_crs": source_crs,
        "address": None,
        "provider": provider,
        "source_update_timestamp": None,
        "retrieval_timestamp": None,
        "provenance": "OFFICIAL",
        "source_provenance": source_provenance,
        "raw_source_reference": None,
        "capacity": None,
        "operating_info": None,
        "access_info": None,
        "disaster_suitability": None,
        "data_quality_flags": [],
    }


def normalize_shelter_row(row: dict[str, Any]) -> dict[str, Any]:
    item = _base("civil-defense-shelter-national", row, "CIVIL_DEFENSE_SHELTER", "행정안전부 / LocalData / 공공데이터포털", "EPSG:4326", "관리번호", "시설명")
    item.update({
        "name": _text(row, "시설명"),
        "latitude": _number(row, "위도(EPSG4326)"),
        "longitude": _number(row, "경도(EPSG4326)"),
        "address": _text(row, "도로명전체주소", "소재지전체주소"),
        "source_update_timestamp": _text(row, "데이터갱신시점", "최종수정시점"),
        "raw_source_reference": "data/raw/localdata/civil_defense_shelter/source.csv",
        "capacity": _number(row, "최대수용인원"),
        "operating_info": _text(row, "운영상태"),
        "disaster_suitability": "민방위 대피시설",
        "facility_position": _text(row, "시설위치(지상/지하)"),
        "area_m2": _number(row, "시설면적(㎡)"),
    })
    if item["latitude"] is None or item["longitude"] is None:
        item["data_quality_flags"].append("NO_VALID_WGS84_COORDINATES")
    if item["capacity"] is None:
        item["data_quality_flags"].append("CAPACITY_MISSING")
    if item["operating_info"] is None:
        item["data_quality_flags"].append("OPERATING_STATUS_MISSING")
    return item


def normalize_water_row(row: dict[str, Any]) -> dict[str, Any]:
    item = _base("emergency-water-national-standard", row, "EMERGENCY_WATER", "행정안전부 / LocalData / 공공데이터포털", "EPSG:5174", "관리번호", "시설명건물명")
    x = _number(row, "좌표정보(X)")
    y = _number(row, "좌표정보(Y)")
    if x is not None and y is not None:
        lon, lat = WATER_TO_WGS84.transform(x, y)
        item["longitude"], item["latitude"] = lon, lat
    item.update({
        "name": _text(row, "시설명건물명", "사업장명"),
        "address": _text(row, "도로명주소", "지번주소"),
        "source_update_timestamp": _text(row, "데이터갱신시점", "최종수정시점"),
        "raw_source_reference": "data/raw/localdata/emergency_water/source.csv",
        "operating_info": _text(row, "상세영업상태명", "영업상태명"),
        "disaster_suitability": "민방위 급수시설",
    })
    if x is None or y is None:
        item["data_quality_flags"].append("PROJECTED_COORDINATES_MISSING")
    item["data_quality_flags"].append("NO_CAPACITY_FIELD_IN_SOURCE")
    return item


def normalize_aed_row(row: dict[str, Any]) -> dict[str, Any]:
    item = _base("aed-anyang-file", row, "AED", "경기도 안양시 / 공공데이터포털", None, "설치기관명", "소재지도로명주소")
    item.update({
        "name": _text(row, "설치기관명"),
        "address": _text(row, "소재지도로명주소"),
        "source_update_timestamp": _text(row, "데이터기준일자"),
        "raw_source_reference": "data/raw/data_go_kr/aed_anyang/source.csv",
        "disaster_suitability": "심정지 응급지원",
    })
    item["data_quality_flags"].append("NO_COORDINATES_IN_SOURCE")
    item["data_quality_flags"].append("ACCESS_INFORMATION_MISSING")
    return item


def _rows(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="cp949", newline="") as handle:
        yield from csv.DictReader(handle)


def load_real_facilities() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in _rows(ROOT / "data/raw/localdata/civil_defense_shelter/source.csv"):
        address = " ".join(str(row.get(field) or "") for field in ("소재지전체주소", "도로명전체주소", "지번주소"))
        if "안양시" in address:
            records.append(normalize_shelter_row(row))
    for row in _rows(ROOT / "data/raw/localdata/emergency_water/source.csv"):
        address = " ".join(str(row.get(field) or "") for field in ("도로명주소", "지번주소"))
        if "안양시" in address:
            records.append(normalize_water_row(row))
    for row in _rows(ROOT / "data/raw/data_go_kr/aed_anyang/source.csv"):
        records.append(normalize_aed_row(row))
    retrievals = {
        "civil-defense-shelter-national": "2026-08-20T11:20:17+00:00",
        "emergency-water-national-standard": "2026-08-20T11:17:51+00:00",
        "aed-anyang-file": "2026-08-20T11:33:08+00:00",
    }
    for record in records:
        record["retrieval_timestamp"] = retrievals[record["source_dataset_id"]]
    return records


def load_processed_facilities() -> list[dict[str, Any]]:
    path = ROOT / "data/processed/anyang_facilities.json"
    if not path.exists():
        raise RuntimeError("processed real facility data is missing; run scripts/data/normalize_facilities.py")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("generated_from") != "data/manifests/data_manifest.json":
        raise RuntimeError("processed facility data is not linked to the manifest")
    records = payload.get("records")
    if not isinstance(records, list) or any(record.get("provenance") != "OFFICIAL" for record in records):
        raise RuntimeError("processed facility data failed the real-data integrity guard")
    return records


def load_local_shelter_context() -> list[dict[str, Any]]:
    """Expose the municipal shelter list as a separate, non-merged context layer."""
    path = ROOT / "data/processed/anyang_local_shelters.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    retrieved_at = payload.get("retrieved_at")
    return [{
        "id": f"anyang-local-civil-defense-shelter-board:{item['source_post_id']}",
        "source_dataset_id": "anyang-local-civil-defense-shelter-board",
        "name": item.get("facility_name"),
        "category": "CIVIL_DEFENSE_SHELTER_LOCAL",
        "latitude": item.get("latitude"),
        "longitude": item.get("longitude"),
        "source_crs": "EPSG:4326",
        "address": item.get("address"),
        "provider": "안양시청",
        "source_update_timestamp": item.get("source_period"),
        "retrieval_timestamp": retrieved_at,
        "provenance": "OFFICIAL",
        "source_provenance": "ANYANG_LOCAL_OFFICIAL",
        "raw_source_reference": "data/raw/goal4b/anyang_local_shelter_pages/",
        "capacity": item.get("capacity_persons"),
        "operating_info": "원문 목록값 보존",
        "data_quality_flags": [],
    } for item in payload.get("items", [])]
