from pathlib import Path

import pytest

from services.ai_surrogate.model import load_bundle, predict_bundle, support_status


MODEL_PATH = Path("models/scenario_triage/model.joblib")


def test_goal5a_model_bundle_is_versioned_and_fail_closed():
    bundle = load_bundle(MODEL_PATH)
    metadata = bundle["metadata"]
    features = {name: value for name, value in zip(metadata["feature_names"], metadata["support_mean"])}
    assert support_status(features, metadata) == "AI_ESTIMATE_SUPPORTED"
    prediction = predict_bundle(bundle, "test-scenario", features)
    assert prediction.support_status == "AI_ESTIMATE_SUPPORTED"
    assert prediction.exact_verified is False
    assert prediction.provenance == "AI_SURROGATE"


def test_goal5a_model_rejects_out_of_support_feature():
    bundle = load_bundle(MODEL_PATH)
    metadata = bundle["metadata"]
    features = {name: value for name, value in zip(metadata["feature_names"], metadata["support_mean"])}
    features[metadata["feature_names"][0]] = metadata["support_upper"][0] + 1.0
    prediction = predict_bundle(bundle, "ood-scenario", features)
    assert prediction.support_status == "AI_ESTIMATE_UNSUPPORTED"
    assert prediction.ranking_score is None


def test_goal5a_model_rejects_missing_feature():
    bundle = load_bundle(MODEL_PATH)
    metadata = bundle["metadata"]
    features = {name: value for name, value in zip(metadata["feature_names"], metadata["support_mean"])}
    features.pop(metadata["feature_names"][0])
    with pytest.raises(ValueError, match="feature schema"):
        support_status(features, metadata)
