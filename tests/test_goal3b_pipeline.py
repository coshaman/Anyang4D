from pathlib import Path

from services.flood.pipeline import evaluate_predictions, run_synthetic_evaluation


def test_metrics_include_error_wet_dry_and_temporal_sanity():
    result = evaluate_predictions(
        [[[0.0, 0.5]], [[0.2, 0.8]]],
        [[[0.0, 0.4]], [[0.3, 0.9]]],
    )
    assert result["mae"] > 0
    assert "rmse" in result
    assert "wet_dry_iou" in result
    assert "temporal_non_decrease_fraction" in result


def test_synthetic_evaluation_writes_provenance_and_metrics(tmp_path: Path):
    result = run_synthetic_evaluation(tmp_path, seed=7)
    assert result["provenance"] == "SYNTHETIC"
    assert result["field_kind"] == "RELATIVE_HAZARD"
    assert (tmp_path / "config.json").exists()
    assert (tmp_path / "metrics.json").exists()
