# Goal 4B decision record

Goal 4B hardens the administrative 4D simulator as a bounded, deterministic training/demo tool. It does not claim a physical flood model, street-level flood depth, AI inference, or citizen emergency routing.

## Frozen boundary

- `FINAL_TERRAIN_CLASS`: `TERRAIN_C`
- `STREET_LEVEL_FLOOD_TERRAIN_PATH`: `DROP`
- `CITIZEN_HAZARD_ROUTING_FROM_TERRAIN`: `DROP`
- PhysicsNeMo, AI hazard inference, and flood-depth estimation: `DROP`

## Data separation

The 2026-07-31 official municipal dong totals remain the population authority: 31 dongs and 562,143 people. Their point locations are `SIMULATED_SPATIAL_ALLOCATION` anchors because the supplied workbook has no dong polygons. Current local municipal shelter, emergency-water, and flood-response inventory extracts are retained separately from filtered national records. The shelter crosswalk is conservative and never merges records operationally.

## Operational semantics

Hazard containment or explicit scenario selection derives affected demand. Participation is an explicit deterministic scenario assumption. Official water capacity is `RESPONSE_RESOURCE_CAPACITY`, not evacuation shelter capacity. Assignment uses exact deterministic NetworkX min-cost flow on the bounded demo graph.
