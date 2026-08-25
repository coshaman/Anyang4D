# Goal 7 decision — optional observation and facility-geometry modules

## Decision

All four optional modules are explicitly rejected for this release. The rejection is evidence-based, not a claim that the models are unusable in general:

| Module | Release status | Required input/evaluation missing |
| --- | --- | --- |
| TerraMind | `REJECTED` | Legally sourced Anyang pre/post EO imagery, flood/burn labels, local evaluation |
| xBD-S12 | `REJECTED` | Legally sourced Sentinel-1/2 pre/post imagery, building-damage labels, local evaluation |
| MapAnything | `REJECTED` | Legally collected 10–20 facility photo sets, manual measurements, metric error report |
| JuPedSim | `REJECTED` | Validated entrance geometry and observed pedestrian-flow calibration |

The machine-readable release contract is available at `/api/admin/optional-modules` and `/api/admin/optional-modules/{module}`. It is admin-only, retains the intended license and role, and prevents any optional output from becoming citizen guidance.

## Safety boundary

No optional model is installed, trained, or exposed as an operational predictor. If inputs later become available, outputs must remain `OBSERVED_AI` or `SIMULATED_ADMIN_SCENARIO` until local evaluation and human review pass. AI output must never automatically create an official road closure, damage declaration, emergency dispatch, or citizen safe route.

## Evidence

- The repository contains no EO imagery, facility photo sets, manual geometry measurements, building-damage labels, or pedestrian-flow observations.
- Existing `TERRAIN_C` and blocked-provider records do not satisfy these modules' input gates.
- Tests: `tests/test_optional_modules_api.py` verifies all four terminal statuses, evidence fields, licenses, and citizen-guidance restrictions.
