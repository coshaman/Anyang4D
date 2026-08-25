import json
from pathlib import Path


def test_release_ai_reproducibility_artifact_passes():
    payload = json.loads(Path("artifacts/evals/release/ai-reproducibility.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["dataset"]["record_count"] == 160
    assert payload["dataset"]["feature_count"] == 28
    assert payload["clean_input_inference"]["support_status"] == "AI_ESTIMATE_SUPPORTED"
