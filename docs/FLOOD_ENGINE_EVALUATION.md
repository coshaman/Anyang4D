# SAFE-Twin flood engine evaluation

The reproducible synthetic evaluation is under `artifacts/evals/ml/goal3b/` and uses seed 7. It is a time-varying 16×16 relative-hazard fixture, not water depth and not Anyang truth.

| Predictor | MAE | RMSE | Wet/dry IoU | Temporal non-decrease |
| --- | ---: | ---: | ---: | ---: |
| SAFE-Twin deterministic Level-A baseline | 0.126813 | 0.156067 | 0.327485 | 1.000000 |
| Persistence comparator | 0.069619 | 0.089077 | 0.653061 | 1.000000 |

Persistence wins on this deliberately short synthetic fixture, so the baseline is not described as a learned model or as validated hydraulics. The result proves pipeline outputs, metric computation, time variation, frame persistence, and provenance handling. A local PhysicsNeMo neural-operator training result was not produced because the isolated Windows installation stalled and the machine has no NVIDIA GPU/driver path; see `artifacts/evals/ml/physicsnemo/environment.json`.
