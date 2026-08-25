# Goal 3A decision

## Decision

Proceed to Goal 3B with a SAFE-Twin-owned, transparent Level A relative-hazard path and an optional PhysicsNeMo surrogate behind the same teacher/validation gate. Do not integrate flood results into the public simulator yet. Do not start Goal 4 routing.

Use SWMM only as a future hydraulic teacher when authoritative Anyang drainage data and observed events are available. A synthetic SWMM case may test software wiring but must remain synthetic.

Do not select LarNO as the production dependency now. Its benchmark is useful for a separately labelled reproduction, but its public repository license evidence is internally inconsistent for a license-safe vendoring decision, and its released labels are commercial-solver-derived Shenzhen/UKEA benchmarks rather than Anyang observations.

## Gate

Current evidence is `NONE`: the official DEM file is metadata-only and rainfall/local flood labels/drainage are blocked. After DEM and rainfall are supplied, the highest defensible target is Level A. Level B requires Anyang flood labels. Level C is deferred until drainage and calibration evidence are present.

The UI may later show “relative scenario hazard” with assumptions, provenance, and an explicit “not predicted depth / not emergency-grade” disclaimer. It must not show a numeric Anyang depth forecast from benchmark or synthetic data.
