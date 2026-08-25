from scripts.model_audit import classify_flood_maturity, license_record, provenance_record


def test_maturity_requires_local_labels_for_level_b():
    assert classify_flood_maturity({"high_resolution_dem": True, "rainfall_timeseries": True})["level"] == "A"
    assert classify_flood_maturity(
        {"high_resolution_dem": True, "rainfall_timeseries": True, "anyang_flood_labels": True}
    )["level"] == "B"


def test_level_c_requires_drainage_and_calibration():
    evidence = {
        "high_resolution_dem": True,
        "rainfall_timeseries": True,
        "anyang_flood_labels": True,
        "authoritative_drainage": True,
        "calibration_observations": True,
    }
    assert classify_flood_maturity(evidence)["level"] == "C"


def test_license_and_provenance_are_explicit():
    item = license_record("PhysicsNeMo", "Apache-2.0", "GO", "https://github.com/NVIDIA/physicsnemo", "framework")
    assert item["status"] == "GO"
    benchmark = provenance_record("LarNO-Futian", "BENCHMARK", "Hugging Face", False, "not Anyang")
    assert benchmark["allowed_for_anyang"] is False
