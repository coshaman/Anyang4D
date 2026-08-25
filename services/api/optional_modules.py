from __future__ import annotations

from fastapi import APIRouter, HTTPException


router = APIRouter(prefix="/api/admin/optional-modules", tags=["admin-optional-modules"])


OPTIONAL_MODULES = [
    {
        "module": "TerraMind",
        "status": "REJECTED",
        "license": "Apache-2.0",
        "role": "post-event Earth-observation flood/burn-scar observation",
        "reason": "No legally sourced Anyang pre/post imagery or local evaluation labels are present; the module cannot produce an evidence-backed observation layer.",
        "evidence": ["no imagery files in the repository", "no Anyang flood/burn validation labels", "no model checkpoint or reproducible evaluation"],
        "output_provenance": "OBSERVED_AI would be required if later integrated",
        "citizen_guidance_authorized": False,
    },
    {
        "module": "xBD-S12",
        "status": "REJECTED",
        "license": "MIT",
        "role": "post-event building-damage candidate mapping",
        "reason": "No legally sourced Sentinel-1/2 pre/post imagery, building labels, or Anyang validation set is present.",
        "evidence": ["no pre/post EO imagery in the repository", "no building-damage labels", "no local precision/recall evaluation"],
        "output_provenance": "OBSERVED_AI would be required if later integrated",
        "citizen_guidance_authorized": False,
    },
    {
        "module": "MapAnything",
        "status": "REJECTED",
        "license": "Apache-2.0",
        "role": "representative shelter-entrance metric geometry",
        "reason": "No legally collected imagery or manual measurements are available, so the required 10–20-set geometry validation cannot be performed.",
        "evidence": ["no facility photo sets in the repository", "no manual measurement ground truth", "no checkpoint run or metric error report"],
        "output_provenance": "OBSERVED_AI would be required if later integrated",
        "citizen_guidance_authorized": False,
    },
    {
        "module": "JuPedSim",
        "status": "REJECTED",
        "license": "LGPLv3",
        "role": "isolated entrance bottleneck micro-simulation",
        "reason": "No validated entrance geometry or observed pedestrian-flow parameters exist; a micro-simulation would add unsupported precision without user benefit.",
        "evidence": ["MapAnything geometry prerequisite is rejected", "no observed flow calibration", "no isolated simulation artifact"],
        "output_provenance": "SIMULATED_ADMIN_SCENARIO only if later integrated",
        "citizen_guidance_authorized": False,
    },
]


@router.get("")
def list_optional_modules() -> dict:
    return {"items": OPTIONAL_MODULES, "policy": "reject modules without legal inputs and evaluation"}


@router.get("/{module}")
def get_optional_module(module: str) -> dict:
    item = next((value for value in OPTIONAL_MODULES if value["module"].lower() == module.lower()), None)
    if item is None:
        raise HTTPException(status_code=404, detail="optional module not found")
    return item

