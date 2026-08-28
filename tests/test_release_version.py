from services.api.main import release_version


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
