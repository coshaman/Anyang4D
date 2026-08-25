import numpy as np

from services.terrain.validation import classify_quality, elevation_metrics, terrain_diagnostics


def test_elevation_metrics_and_frozen_classification():
    metrics = elevation_metrics(np.array([100.0, 102.0, 110.0]), np.array([101.0, 101.0, 108.0]))
    assert metrics["count"] == 3
    assert metrics["mae_m"] == 4 / 3
    assert metrics["p95_abs_error_m"] == 1.9
    assert classify_quality({"spot": {"mae_m": 1, "p95_abs_error_m": 2}, "contour_p95_m": 1, "seam_p95_m": 1, "seam_median_m": 0.5, "road_p95_m": 10, "coverage": 1, "slope_p99": 1}) == "TERRAIN_A"


def test_diagnostics_identify_invalid_and_slope_values():
    report = terrain_diagnostics(np.array([[1.0, 2.0], [3.0, np.nan]]), 1.0)
    assert report["valid_cell_count"] == 3
    assert report["invalid_cell_count"] == 1
    assert report["slope_p99"] > 0
    assert "flow_direction_counts" in report
    assert "flow_accumulation_max" in report
