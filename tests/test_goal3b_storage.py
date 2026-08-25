from pathlib import Path

from services.flood.baseline import run_level_a_baseline
from services.flood.contracts import FloodScenarioInput, Provenance
from services.flood.storage import FrameStore


def test_frame_store_round_trips_metadata_and_time_frame(tmp_path: Path):
    scenario = FloodScenarioInput(
        scenario_id="storage-fixture",
        dem=[[2.0, 1.0], [1.0, 0.0]],
        rainfall_mm_per_timestep=[10.0, 20.0],
        timestep_minutes=5,
        duration_steps=2,
        grid_resolution_m=1.0,
        crs="EPSG:5174",
        transform=[1, 0, 0, 0, -1, 0],
        rainfall_mode="SCENARIO",
        provenance=Provenance.SYNTHETIC,
    )
    store = FrameStore(tmp_path)
    store.save(run_level_a_baseline(scenario))
    assert store.list_times("storage-fixture") == [0, 5]
    assert store.read_frame("storage-fixture", 5)["field_kind"] == "RELATIVE_HAZARD"
    assert store.read_frame("storage-fixture", 5)["provenance"] == "SYNTHETIC"


def test_frame_store_rejects_path_traversal(tmp_path: Path):
    store = FrameStore(tmp_path)
    try:
        store.metadata("../escape")
    except ValueError:
        pass
    else:
        raise AssertionError("path traversal must be rejected")
