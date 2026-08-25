import json
from pathlib import Path


def test_goal6a_release_audit_passes():
    payload = json.loads(Path("artifacts/evals/release/goal6a-release-audit.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["release_classification"] == "COMPETITION_RELEASE_B"
