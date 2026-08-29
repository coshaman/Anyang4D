from services.api.main import release_version
from services.api.main import healthz


def test_release_version_contains_deployment_identity_fields():
    payload = release_version()
    assert set(payload) >= {
        "git_commit",
        "build_timestamp",
        "frontend_build_id",
        "api_schema_version",
        "scenario_schema_version",
    }
    assert payload["frontend_build_id"]


def test_release_version_without_commit_metadata_does_not_block_startup(monkeypatch):
    monkeypatch.delenv("SAFE_TWIN_GIT_COMMIT", raising=False)
    assert release_version()["git_commit"] == "unknown"


def test_release_version_with_full_commit_metadata_does_not_change_startup_contract(monkeypatch):
    commit = "0123456789abcdef0123456789abcdef01234567"
    monkeypatch.setenv("SAFE_TWIN_GIT_COMMIT", commit)
    payload = release_version()
    assert payload["git_commit"] == commit
    assert payload["frontend_build_id"] == commit


def test_healthz_contract_is_independent_of_optional_commit_metadata(monkeypatch):
    monkeypatch.delenv("SAFE_TWIN_GIT_COMMIT", raising=False)
    assert healthz()["status"] == "ok"
    monkeypatch.setenv("SAFE_TWIN_GIT_COMMIT", "0123456789abcdef0123456789abcdef01234567")
    assert healthz()["status"] == "ok"
