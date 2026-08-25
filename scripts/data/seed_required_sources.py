from __future__ import annotations

from scripts.data.audit_sources import SourceStatus
from scripts.data.record_status import upsert


def blocked(id: str, title: str, provider: str, landing: str, endpoint: str, blocker: str, env: str, fallback: str) -> dict:
    return {
        "id": id, "dataset_title": title, "provider": provider, "landing_url": landing,
        "actual_download_url": endpoint, "status": SourceStatus.HUMAN_AUTH_REQUIRED.value,
        "auth_requirement": "provider access key/application required",
        "blocker": blocker, "required_action": f"obtain the provider credential and set {env}",
        "expected_env_var": env, "safe_fallback": fallback,
    }


def main() -> None:
    records = [
        blocked("earthquake-outdoor-shelter", "전국지진옥외대피장소표준데이터", "행정안전부 / 국민재난안전포털",
                "https://www.data.go.kr/data/15072620/standard.do", "https://www.safetydata.go.kr/disaster-data/downloadData?dataSn=1339",
                "official download endpoint returned HTTP 405 for GET and HTTP 415 for form POST; provider download flow requires its supported session/request", "SAFETYDATA_SERVICE_KEY", "use the already downloaded civil-defense shelter source only as a distinct shelter type; do not substitute it"),
        blocked("emergency-medical-institutions", "경기도 응급의료기관 및 응급의료지원센터 현황", "경기도",
                "https://www.data.go.kr/data/15057684/openapi.do", "https://data.gg.go.kr/portal/data/service/selectServicePage.do?page=1&sortColumn=&sortDirection=&infId=MB714IBPDSE5OPNIMW0V27143432&infSeq=3",
                "official portal documents an application-controlled linked service; no public file download was exposed in the page", "GYEONGGI_DATA_API_KEY", "use source metadata only until provider access is supplied"),
        blocked("emergency-alerts", "긴급재난문자 발송 현황", "행정안전부 / 국민재난안전포털",
                "https://www.data.go.kr/", "https://www.safetydata.go.kr/",
                "official service is exposed through provider-controlled disaster-data access; no unauthenticated raw export was exposed", "SAFETYDATA_SERVICE_KEY", "retain alert ingestion as a future adapter; do not fabricate historical alerts"),
        blocked("kma-weather", "기상청 단기예보 조회서비스", "기상청",
                "https://www.data.go.kr/data/15084084/openapi.do", "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst",
                "actual request without ServiceKey returned HTTP 401 SERVICE_KEY_IS_NULL", "KMA_SERVICE_KEY", "use no weather features until the key is supplied"),
        blocked("flood-traces", "침수흔적도 / 재해정보지도", "국가재난안전포털 및 지방자치단체",
                "https://www.safetydata.go.kr/", "https://www.data.go.kr/",
                "no official Anyang raw vector download was exposed by the searched public catalogs; neighboring-city records are not an acceptable substitute", "FLOOD_TRACE_SOURCE_URL", "Goal 3 must remain a documented viability decision, not a fabricated layer"),
        blocked("gis-buildings", "건물 공간정보", "국토교통부 국가공간정보센터 / VWorld",
                "https://www.data.go.kr/data/15057570/openapi.do", "https://api.vworld.kr/req/data",
                "actual request without key returned PARAM_REQUIRED: key", "VWORLD_API_KEY", "OSM building tags may be used only as a clearly labeled incomplete fallback"),
        blocked("sgis-population", "SGIS 인구 격자 / 집계구 인구", "통계청 국가통계정보처",
                "https://www.data.go.kr/data/15021230/openapi.do", "https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json",
                "official authentication endpoint redirected to sgisapi.mods.go.kr and returned HTTP 412 for missing required parameters", "SGIS_SERVICE_KEY", "do not infer population from unrelated administrative totals"),
        blocked("environment-land-cover", "환경공간정보 토지피복지도", "환경부 환경공간정보서비스",
                "https://www.data.go.kr/", "https://egis.me.go.kr/",
                "official service is a provider-controlled spatial service; no raw Anyang package was publicly exposed during acquisition", "EGIS_ACCESS_TOKEN", "do not replace land cover with OSM landuse tags without labeling it a proxy"),
        blocked("dem-terrain", "국가 수치표고모델(DEM)", "국토교통부 국토지리정보원",
                "https://map.ngii.go.kr/", "https://map.ngii.go.kr/ms/map/NlipMap.do",
                "official high-resolution Korean DEM distribution is controlled by the national geospatial download service; no unauthenticated Anyang package was exposed", "NGII_ACCESS_TOKEN", "do not silently substitute a coarse global DEM for the required terrain source"),
        {
            "id": "fire-water-standard", "dataset_title": "전국소방용수시설표준데이터", "provider": "소방청 / 공공데이터포털",
            "landing_url": "https://www.data.go.kr/data/15034538/standard.do",
            "actual_download_url": "https://api.data.go.kr/openapi/tn_pubr_public_ffus_wtrcns_api",
            "status": SourceStatus.HUMAN_AUTH_REQUIRED.value, "auth_requirement": "service key required",
            "blocker": "actual request returned HTTP 401 SERVICE_KEY_IS_NULL", "required_action": "obtain a data.go.kr service key and set DATA_GO_KR_SERVICE_KEY",
            "expected_env_var": "DATA_GO_KR_SERVICE_KEY", "safe_fallback": "none; do not infer fire-water locations from addresses",
        },
    ]
    for record in records:
        upsert(record)


if __name__ == "__main__":
    main()
