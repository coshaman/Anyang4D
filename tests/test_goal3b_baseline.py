import numpy as np

from services.flood.baseline import run_level_a_baseline
from services.flood.contracts import FloodScenarioInput, Provenance


def scenario(rainfall=(10.0, 20.0)):
    return FloodScenarioInput(
        scenario_id="fixture",
        dem=[[3.0, 2.0, 1.0], [3.0, 0.0, 1.0], [4.0, 2.0, 2.0]],
        crs="EPSG:5174",
        grid_resolution_m=1.0,
        transform=[1, 0, 0, 0, -1, 0],
        rainfall_mm_per_timestep=list(rainfall),
        timestep_minutes=5,
        duration_steps=len(rainfall),
        rainfall_mode="SCENARIO",
        provenance=Provenance.SYNTHETIC,
    )


def test_lower_terrain_has_higher_relative_hazard():
    output = run_level_a_baseline(scenario((10.0,)))
    frame = np.asarray(output.frames[0], dtype=float)
    assert frame[1, 1] > frame[0, 0]


def test_cumulative_rainfall_is_monotonic_without_recession():
    output = run_level_a_baseline(scenario((5.0, 20.0, 30.0)))
    center = [frame[1][1] for frame in output.frames]
    assert center[0] <= center[1] <= center[2]


def test_nodata_and_alignment_metadata_are_preserved():
    item = scenario((10.0,))
    item.dem[0][1] = None
    output = run_level_a_baseline(item)
    assert output.frames[0][0][1] is None
    assert output.crs == item.crs
    assert output.transform == item.transform
    assert output.grid_resolution_m == item.grid_resolution_m
