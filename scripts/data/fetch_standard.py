from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests

from .fetch_sources import ROOT, load_manifest, save_manifest, sha256_file, utc_now, upsert_record
from .audit_sources import SourceStatus


def fetch_standard(public_data_pk: str, *, per_page: int = 10000) -> tuple[dict[str, Any], dict[str, Any]]:
    session = requests.Session()
    session.headers.update({"User-Agent": "SAFE-Twin-Anyang-data-audit/0.1"})
    header_url = f"https://www.data.go.kr/download/columList.json?pk={public_data_pk}&ext=JSON"
    header_response = session.get(header_url, timeout=60)
    header_response.raise_for_status()
    header = header_response.json()
    table = header["tableVO"]
    total = int(header.get("totalCount") or 0)
    records: list[dict[str, Any]] = []
    for page in range(1, max(1, (total + per_page - 1) // per_page) + 1):
        params: list[tuple[str, Any]] = [
            ("publicDataPk", public_data_pk),
            ("svcTableNm", table["svcTableNm"]),
            ("perPage", per_page),
            ("page", page),
        ]
        params.extend(("colNmList", column) for column in table["colNmList"])
        response = session.get("https://www.data.go.kr/download/standard.json", params=params, timeout=120)
        response.raise_for_status()
        page_records = response.json()
        if not isinstance(page_records, list):
            raise ValueError(f"unexpected standard data response for {public_data_pk}: {type(page_records).__name__}")
        records.extend(page_records)
        if len(page_records) < per_page:
            break
    return header, {"fields": header["columList"], "records": records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--landing-url", required=True)
    parser.add_argument("--public-data-pk", required=True)
    parser.add_argument("--raw-path", required=True)
    parser.add_argument("--license", default="RECHECK_PROVIDER_TERMS")
    args = parser.parse_args()

    destination = ROOT / args.raw_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "id": args.id,
        "dataset_title": args.title,
        "provider": args.provider,
        "landing_url": args.landing_url,
        "actual_download_url": f"https://www.data.go.kr/download/standard.json?publicDataPk={args.public_data_pk}",
        "license_terms": args.license,
        "auth_requirement": "none observed for standard download",
        "retrieval_timestamp": utc_now(),
        "crs": None,
        "temporal_coverage": None,
        "anyang_feature_count": None,
        "preprocessing_script": "scripts/data/audit_standard.py",
        "status": SourceStatus.FAILED.value,
    }
    try:
        header, data = fetch_standard(args.public_data_pk)
        destination.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        record.update(
            {
                "status": SourceStatus.DOWNLOADED.value,
                "retrieved_at": utc_now(),
                "local_path": destination.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(destination),
                "bytes": destination.stat().st_size,
                "source_record_count": len(data["records"]),
                "source_columns": [column["columNm"] for column in header["columList"]],
                "source_column_codes": [column["columCode"] for column in header["columList"]],
                "source_updated_at": None,
            }
        )
    except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
        record["error"] = str(exc)
    manifest = load_manifest()
    upsert_record(manifest, record)
    save_manifest(manifest)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
