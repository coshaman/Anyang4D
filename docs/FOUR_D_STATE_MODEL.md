# SAFE-Twin Anyang Goal 4A 4D state model

Goal 4A models a hazard-agnostic `WorldState(t, scenario)` with separate hazard, road, facility, demand, and resource state. It is a deterministic administrative what-if engine, not a flood predictor.

`DemandState` uses the official Anyang 2026-07-31 administrative-dong resident totals: 31 units and 562,143 residents, foreign residents excluded. The workbook has no dong polygons, so coordinates are explicitly `SIMULATED_SPATIAL_ALLOCATION_UNIFORM_DONG_ANCHOR`; they are routing anchors, not census-grid truth.

## Scenario contract

`Scenario` stores ID/title, disaster type (`FLOOD`, `EARTHQUAKE`, `FIRE`, `CIVIL_DEFENSE`, `GENERAL_EVACUATION`), ISO start/end, timestep, provenance, assumptions, stepwise hazard keyframes, road closure events, facility availability events, capacity overrides, demand units, resource availability events, eligible facility IDs, and audit log.

Keyframes use stepwise resolution: the latest keyframe at or before the requested frame is active. Polygon, multipolygon, point-radius, corridor, explicit edge closure, and explicit facility closure representations are supported. Scenario geometry is labeled `가정 침수영역`/`훈련/가정 시나리오`; it is never water depth or real emergency guidance.

At each frame the engine recomputes hazard geometry, road availability/reasons, facility availability/effective capacity, resource availability, and capacity-constrained assignments. Thus changing time changes computed city state rather than only a timestamp.
