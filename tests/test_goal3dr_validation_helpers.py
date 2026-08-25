from pathlib import Path

from services.terrain.contracts import ElevationConstraint
from services.terrain.rescue_validation import frozen_plan_sha256, spatial_group_key, seam_statistics, spatial_group_split


def test_frozen_validation_plan_hash_matches_recorded_hash():
    plan = Path("docs/TERRAIN_VALIDATION_PLAN.md")
    recorded = Path("artifacts/evals/terrain/goal3dr/frozen-validation-plan.sha256").read_text(encoding="utf-8").split()[0]
    assert frozen_plan_sha256(plan) == recorded


def test_spatial_group_key_is_deterministic_for_train_test_separation():
    assert spatial_group_key((24.9, 25.1), 25) != spatial_group_key((25.1, 25.1), 25)


def test_seam_statistics_uses_identical_sample_locations():
    result = seam_statistics([100, 101, 102], [101, 101, 103])
    assert result["count"] == 3
    assert result["median_m"] == 1.0
    assert result["p95_m"] >= 1.0


def test_spatial_group_split_has_no_train_test_spot_overlap():
    records = [{"id": "a", "x": 1.0, "y": 1.0}, {"id": "b", "x": 1.5, "y": 1.5}, {"id": "c", "x": 30.0, "y": 1.0}]
    train, test = spatial_group_split(records, {"a"}, 25.0)
    assert {item["id"] for item in train}.isdisjoint({item["id"] for item in test})
    assert [item["id"] for item in test] == ["a", "b"]
    assert [item["id"] for item in train] == ["c"]
