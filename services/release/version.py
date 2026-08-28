from __future__ import annotations

import os


def release_version() -> dict[str, str]:
    """Return deployment identity shared by the API and frontend build."""
    commit = os.getenv("SAFE_TWIN_GIT_COMMIT", "unknown")
    frontend_build_id = os.getenv("SAFE_TWIN_FRONTEND_BUILD_ID", commit if commit != "unknown" else "local-dev")
    return {
        "git_commit": commit,
        "build_timestamp": os.getenv("SAFE_TWIN_BUILD_TIMESTAMP", "unknown"),
        "frontend_build_id": frontend_build_id,
        "api_schema_version": os.getenv("SAFE_TWIN_API_SCHEMA_VERSION", "1"),
        "scenario_schema_version": os.getenv("SAFE_TWIN_SCENARIO_SCHEMA_VERSION", "1"),
    }
