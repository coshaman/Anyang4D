from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/goal4b/anyang_local_shelter_pages"
OUT = ROOT / "data/processed/anyang_local_shelters.json"


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(value))).strip()


def parse_page(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    records = []
    for row in re.findall(r"<tr>(.*?)</tr>", text, flags=re.S | re.I):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S | re.I)
        if len(cells) < 6 or not clean(cells[0]).isdigit():
            continue
        button = re.search(r'data-title="([^"]*)".*?data-lat="([^"]*)".*?data-lng="([^"]*)"', row, flags=re.S | re.I)
        post = re.search(r"nttNo=(\d+)", row, flags=re.I)
        records.append({
            "source_post_id": post.group(1) if post else None,
            "row_number": int(clean(cells[0])),
            "dong_name": clean(cells[1]),
            "facility_name": clean(cells[2]),
            "address": clean(cells[3]),
            "area_m2": float(clean(cells[4]).replace(",", "")) if clean(cells[4]).replace(",", "").replace(".", "", 1).isdigit() else None,
            "capacity_persons": int(float(clean(cells[5]).replace(",", ""))) if clean(cells[5]).replace(",", "").isdigit() else None,
            "latitude": float(button.group(2)) if button else None,
            "longitude": float(button.group(3)) if button else None,
            "provenance": "ANYANG_LOCAL_OFFICIAL",
            "source_period": "current municipal shelter list",
        })
    return records


pages = sorted(RAW.glob("page-*.html"))
items = [item for page in pages for item in parse_page(page)]
payload = {
    "schema_version": "0.1.0",
    "provider": "안양시청",
    "dataset_title": "민방위 대피시설 목록",
    "source_url": "https://m.anyang.go.kr/main/selectBbsNttList.do?bbsNo=1604&key=4047",
    "retrieved_at": datetime.now(timezone.utc).isoformat(),
    "source_files": [{"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in pages],
    "record_count": len(items),
    "items": items,
    "provenance": "ANYANG_LOCAL_OFFICIAL",
    "notes": ["시설 면적·대피 가능 인원은 시청 목록 값 보존", "주소와 지도 좌표는 원문 그대로 보존", "국가 표준데이터와 자동 병합하지 않음"],
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"pages": len(pages), "record_count": len(items), "unique_source_post_ids": len({item['source_post_id'] for item in items})}, ensure_ascii=False))
