from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from services.flood.baseline import run_level_a_baseline
from services.flood.contracts import FloodScenarioInput, Provenance
from services.flood.storage import FrameStore


ROOT = Path(__file__).resolve().parents[2]
STORE = FrameStore(ROOT / "artifacts/evals/ml/goal3b/frames")
router = APIRouter(prefix="/api/internal/simulations", tags=["internal-simulation-lab"])


def _ensure_demo() -> None:
    try:
        STORE.metadata("anyang-demo-synthetic")
        return
    except FileNotFoundError:
        pass
    scenario = FloodScenarioInput(
        scenario_id="anyang-demo-synthetic",
        dem=[[3, 2, 2, 3], [2, 1, 0, 2], [3, 2, 1, 3], [4, 3, 2, 3]],
        rainfall_mm_per_timestep=[10, 20, 35, 50],
        timestep_minutes=5,
        duration_steps=4,
        grid_resolution_m=1,
        crs="EPSG:5174",
        transform=[1, 0, 0, 0, -1, 0],
        rainfall_mode="SCENARIO",
        provenance=Provenance.SYNTHETIC,
    )
    STORE.save(run_level_a_baseline(scenario))


@router.get("")
def list_simulations() -> dict:
    _ensure_demo()
    return {"items": STORE.list_scenarios()}


@router.get("/{scenario_id}")
def simulation_metadata(scenario_id: str) -> dict:
    _ensure_demo()
    try:
        return STORE.metadata(scenario_id)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=404, detail="simulation not found") from exc


@router.get("/{scenario_id}/times")
def simulation_times(scenario_id: str) -> dict:
    _ensure_demo()
    try:
        return {"scenario_id": scenario_id, "times": STORE.list_times(scenario_id)}
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=404, detail="simulation not found") from exc


@router.get("/{scenario_id}/frames/{time}")
def simulation_frame(scenario_id: str, time: int) -> dict:
    _ensure_demo()
    try:
        return STORE.read_frame(scenario_id, time)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=404, detail="frame not found") from exc
