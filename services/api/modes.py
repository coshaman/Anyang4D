from __future__ import annotations

from fastapi import APIRouter, HTTPException


router = APIRouter(prefix="/api/admin/modes", tags=["admin-mode-contracts"])


MODE_CONTRACTS = [
    {
        "mode": "FLOOD",
        "label": "침수 훈련",
        "source_status": "ADMIN_SCENARIO",
        "sources": ["관리자 입력 침수영역", "공식 대피소·인구·보행 그래프"],
        "supported_calculations": ["시간별 가정 영역", "도로·시설 영향", "용량 제약 대피 배정"],
        "unsupported_claims": ["terrain-derived flood depth", "official flood forecast", "citizen safe route"],
        "citizen_guidance_authorized": False,
    },
    {
        "mode": "EARTHQUAKE",
        "label": "지진 훈련",
        "source_status": "HUMAN_AUTH_REQUIRED",
        "sources": ["지진 옥외대피장소 원자료(접근 필요)", "관리자 통제 도로·가정 영역"],
        "supported_calculations": ["관리자 입력 영역", "수동 도로 통제", "확보된 대피소 기준 용량 배정"],
        "unsupported_claims": ["building collapse probability", "official earthquake forecast", "automatic road closure"],
        "citizen_guidance_authorized": False,
    },
    {
        "mode": "FIRE",
        "label": "화재 훈련",
        "source_status": "HUMAN_AUTH_REQUIRED",
        "sources": ["관리자 입력 화재영역", "소방용수·응급의료 원자료(접근 필요)", "보행 그래프"],
        "supported_calculations": ["관리자 입력 영역 회피", "수동 도로 통제", "대피소 용량 배정"],
        "unsupported_claims": ["building fire spread", "fire arrival time", "automatic dispatch"],
        "citizen_guidance_authorized": False,
    },
    {
        "mode": "CIVIL_DEFENSE",
        "label": "민방위 훈련",
        "source_status": "OFFICIAL_CONTEXT",
        "sources": ["안양시 민방위 대피시설 224건", "국가 필터 대피시설 231건", "급수시설 맥락"],
        "supported_calculations": ["대피소 용량 배정", "급수시설을 대응자원 맥락으로 표시", "관리자 가정 도로 통제"],
        "unsupported_claims": ["official emergency alert", "water-resource dispatch optimization", "citizen safe route"],
        "citizen_guidance_authorized": False,
    },
    {
        "mode": "AED",
        "label": "AED 지원",
        "source_status": "OFFICIAL_FILE",
        "sources": ["안양시 AED 파일 305건", "119 긴급신고"],
        "supported_calculations": ["주소 기반 AED 검색", "119 우선 행동 안내"],
        "unsupported_claims": ["live AED availability", "AED coordinates", "medical diagnosis"],
        "first_action": "119",
        "citizen_guidance_authorized": True,
    },
]


@router.get("")
def list_modes() -> dict:
    return {"items": MODE_CONTRACTS, "provenance": "BOUNDARY_MANIFEST"}


@router.get("/{mode}")
def get_mode(mode: str) -> dict:
    item = next((value for value in MODE_CONTRACTS if value["mode"] == mode.upper()), None)
    if item is None:
        raise HTTPException(status_code=404, detail="mode not found")
    return item

