from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.data.audit_sources import SourceStatus, validate_record


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/manifests/data_manifest.json"


def upsert(record: dict[str, Any]) -> None:
    validate_record(record)
    payload = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"schema_version": "0.1.0", "datasets": []}
    datasets = [item for item in payload.get("datasets", []) if item.get("id") != record["id"]]
    datasets.append(record)
    payload["datasets"] = datasets
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def human_action_record(*, dataset_id: str, title: str, provider: str, landing_url: str, attempted_url: str,
                        blocker: str, required_action: str, safe_fallback: str, notes: str = "") -> dict[str, Any]:
    return {
        "id": dataset_id,
        "dataset_title": title,
        "provider": provider,
        "landing_url": landing_url,
        "actual_download_url": attempted_url,
        "status": SourceStatus.HUMAN_AUTH_REQUIRED.value,
        "auth_requirement": "documented by an actual request response",
        "blocker": blocker,
        "required_action": required_action,
        "safe_fallback": safe_fallback,
        "notes": notes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("record_json", type=Path)
    args = parser.parse_args()
    upsert(json.loads(args.record_json.read_text(encoding="utf-8")))


if __name__ == "__main__":
    main()
