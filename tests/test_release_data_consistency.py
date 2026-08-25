import json
from pathlib import Path


def test_release_data_consistency_artifact_passes():
    payload = json.loads(Path("artifacts/evals/release/data-consistency.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert all(payload["checks"].values())
    assert payload["counts"]["local_shelters"] == 224
    assert payload["counts"]["national_filtered_shelters"] == 231
    assert payload["counts"]["local_water"] == 46
    assert payload["counts"]["response_inventory"] == 33
