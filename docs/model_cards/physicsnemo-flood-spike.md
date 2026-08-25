# PhysicsNeMo flood spike

Status: `BLOCKED_ENVIRONMENT` (2026-08-21).

PhysicsNeMo is license-safe for evaluation under Apache-2.0 and has relevant neural-operator/PINO shallow-water examples. The project environment has neither PyTorch nor PhysicsNeMo installed, so the probe did not execute a forward/loss step and produced no flood result. The reproducible probe is `scripts/evals/physicsnemo_probe.py`; evidence is `artifacts/evals/ml/physicsnemo/physicsnemo_probe.json`.

The next isolated run must use synthetic shallow-water tensors only, verify a finite loss and one optimizer step, and keep the result under `SYNTHETIC` provenance. It must not enter the Anyang API until an Anyang teacher, labels, and maturity gate exist.
