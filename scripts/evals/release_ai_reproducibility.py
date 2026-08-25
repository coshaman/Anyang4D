from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import joblib
import sklearn

from services.ai_surrogate.dataset import load_rows
from services.ai_surrogate.explain import explain_features
from services.ai_surrogate.model import load_bundle, predict_bundle


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/evals/release/ai-reproducibility.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    rows = load_rows(ROOT / "data/derived/ai_scenario_surrogate/labels.jsonl")
    bundle = load_bundle(ROOT / "models/scenario_triage/model.joblib")
    metadata = bundle["metadata"]
    first = rows[0]
    features = first["features"]
    prediction = predict_bundle(bundle, first["scenario_id"], features, explain_features(features, metadata))
    split = metadata["evaluation"]["split"]
    dataset_manifest = json.loads((ROOT / "data/derived/ai_scenario_surrogate/manifest.json").read_text(encoding="utf-8"))
    result = {
        "schema_version": "goal6a-ai-reproducibility-v1",
        "status": "PASS",
        "runtime": {"python": platform.python_version(), "scikit_learn": sklearn.__version__, "joblib": joblib.__version__, "platform": platform.platform()},
        "dataset": {"record_count": len(rows), "unique_ids": len({row["scenario_id"] for row in rows}), "feature_count": len(first["features"]), "feature_schema_version": metadata["feature_schema_version"], "manifest_source_hashes": dataset_manifest["source_hashes"], "reference_engine_version": dataset_manifest["reference_engine_version"], "seed": 5},
        "model": {"model_version": metadata["model_bundle_version"], "model_name": metadata["model_name"], "model_sha256": sha256(ROOT / "models/scenario_triage/model.joblib"), "metadata_sha256": sha256(ROOT / "models/scenario_triage/metadata.json"), "training_seed": 17, "train_ids": split["train"], "validation_ids": split["validation"], "test_ids": split["test"], "ood_ids": split["ood"]},
        "clean_input_inference": {"scenario_id": first["scenario_id"], "support_status": prediction.support_status, "exact_verified": prediction.exact_verified, "provenance": prediction.provenance, "ranking_score_present": prediction.ranking_score is not None},
        "reproduction_chain": ["labels.jsonl", "feature extraction already persisted in each row", "version-checked joblib load", "feature-schema validation", "CPU inference"],
    }
    if result["dataset"]["record_count"] != 160 or result["dataset"]["unique_ids"] != 160 or result["dataset"]["feature_count"] != 28 or result["clean_input_inference"]["support_status"] != "AI_ESTIMATE_SUPPORTED":
        result["status"] = "FAIL"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "record_count": len(rows), "feature_count": len(first["features"]), "model_sha256": result["model"]["model_sha256"]}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
