from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

try:
    from .audit_sources import SourceStatus, validate_record
except ImportError:  # direct `python scripts/data/fetch_sources.py` execution
    from audit_sources import SourceStatus, validate_record


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "manifests" / "data_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def download_raw(url: str, destination: Path, *, timeout: int = 60, referer: str | None = None) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(
        url,
        timeout=timeout,
        allow_redirects=True,
        headers={"User-Agent": "SAFE-Twin-Anyang-data-audit/0.1", "Referer": referer or "https://www.data.go.kr/"},
    )
    response.raise_for_status()
    destination.write_bytes(response.content)
    return {
        "actual_download_url": response.url,
        "retrieved_at": utc_now(),
        "http_status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "local_path": destination.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(destination),
        "bytes": destination.stat().st_size,
    }


def load_manifest() -> dict[str, Any]:
    if not MANIFEST.exists():
        return {"schema_version": "0.2.0", "generated_at": utc_now(), "datasets": []}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def upsert_record(manifest: dict[str, Any], record: dict[str, Any]) -> None:
    validate_record(record)
    datasets = manifest.setdefault("datasets", [])
    for index, existing in enumerate(datasets):
        if existing.get("id") == record.get("id"):
            datasets[index] = record
            return
    datasets.append(record)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch one official SAFE-Twin source URL without mutating raw bytes.")
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--landing-url", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--raw-path", required=True)
    parser.add_argument("--license", default="RECHECK_PROVIDER_TERMS")
    parser.add_argument("--auth", default="UNKNOWN")
    args = parser.parse_args()

    manifest = load_manifest()
    record: dict[str, Any] = {
        "id": args.id,
        "dataset_title": args.title,
        "provider": args.provider,
        "landing_url": args.landing_url,
        "actual_download_url": args.url,
        "license_terms": args.license,
        "auth_requirement": args.auth,
        "status": SourceStatus.FAILED.value,
        "retrieval_timestamp": utc_now(),
        "crs": None,
        "temporal_coverage": None,
        "anyang_feature_count": None,
        "preprocessing_script": "scripts/data/audit_sources.py",
    }
    try:
        record.update(download_raw(args.url, ROOT / args.raw_path, referer=args.landing_url))
        record["status"] = SourceStatus.DOWNLOADED.value
    except requests.RequestException as exc:
        record["error"] = str(exc)
    upsert_record(manifest, record)
    save_manifest(manifest)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
