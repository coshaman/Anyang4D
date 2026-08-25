from enum import Enum
from typing import Any


class SourceStatus(str, Enum):
    DOWNLOADED = "DOWNLOADED"
    UP_TO_DATE = "UP_TO_DATE"
    HUMAN_AUTH_REQUIRED = "HUMAN_AUTH_REQUIRED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    SCHEMA_CHANGED = "SCHEMA_CHANGED"
    INSUFFICIENT_FOR_MODEL = "INSUFFICIENT_FOR_MODEL"
    INTENTIONALLY_EXCLUDED = "INTENTIONALLY_EXCLUDED"
    FAILED = "FAILED"


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    status = record.get("status")
    allowed = {item.value for item in SourceStatus}
    if status not in allowed:
        raise ValueError(f"unknown source status: {status}")
    required = {"dataset_title", "provider", "landing_url", "status"}
    missing = sorted(required.difference(record))
    if missing:
        raise ValueError(f"source record missing required fields: {', '.join(missing)}")
    return record


def human_action_block(*, source: str, url: str, why: str, blocker: str, env: str, fallback: str) -> str:
    return "\n".join(
        [
            "HUMAN_ACTION_REQUIRED",
            f"- Source: {source}",
            f"- Exact URL: {url}",
            f"- Why needed: {why}",
            f"- Actual blocker encountered: {blocker}",
            f"- Exact human action: obtain access through the provider's documented account/key/application flow.",
            f"- Expected env var or local file afterward: {env}",
            f"- Safe fallback: {fallback}",
            "- Work continuing: independent sources remain in progress.",
        ]
    )
