import pytest
from pydantic import ValidationError

from services.flood.contracts import FloodScenarioInput, FloodScenarioOutput, Provenance, validate_output_claim


def test_scenario_input_requires_explicit_rainfall_mode_and_provenance():
    scenario = FloodScenarioInput(
        scenario_id="synthetic-demo",
        dem=[[3.0, 2.0], [1.0, 0.0]],
        rainfall_mm_per_timestep=[10.0, 20.0],
        timestep_minutes=5,
        duration_steps=2,
        grid_resolution_m=1.0,
        crs="EPSG:5174",
        transform=[1, 0, 0, 0, -1, 0],
        rainfall_mode="SCENARIO",
        provenance=Provenance.SYNTHETIC,
    )
    assert scenario.rainfall_mode == "SCENARIO"


def test_depth_output_is_rejected_below_level_c():
    with pytest.raises(ValueError):
        validate_output_claim("WATER_DEPTH_M", "A", Provenance.SYNTHETIC)


def test_output_keeps_alignment_and_fidelity_metadata():
    output = FloodScenarioOutput(
        scenario_id="synthetic-demo",
        times=[0, 5],
        field_kind="RELATIVE_HAZARD",
        frames=[[[0.0, 1.0], [0.5, 0.2]], [[0.1, 1.0], [0.6, 0.3]]],
        crs="EPSG:5174",
        transform=[1, 0, 0, 0, -1, 0],
        grid_resolution_m=1.0,
        provenance=Provenance.SYNTHETIC,
        fidelity_level="A",
        backend="safetwin-deterministic-v1",
        assumptions=["no drainage model"],
    )
    assert output.field_kind == "RELATIVE_HAZARD"
    assert output.fidelity_level == "A"
