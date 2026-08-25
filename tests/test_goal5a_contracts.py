import pytest

from services.ai_surrogate.contracts import SurrogatePrediction, validate_feature_schema


def test_prediction_defaults_to_unverified_surrogate_estimate():
    result = SurrogatePrediction("scenario-1").to_dict()
    assert result["exact_verified"] is False
    assert result["provenance"] == "AI_SURROGATE"


def test_feature_schema_fails_closed():
    with pytest.raises(ValueError, match="feature schema mismatch"):
        validate_feature_schema({"a": 1.0}, ["a", "b"])
