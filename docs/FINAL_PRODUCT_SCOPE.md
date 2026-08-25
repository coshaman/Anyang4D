# SAFE-Twin Anyang — final product scope

SAFE-Twin Anyang is a 4D administrative multi-hazard What-if decision-support system. It recomputes time-changing road, facility, evacuation-demand, and response-resource states from Anyang public data, applies capacity-constrained exact assignment, and uses an AI surrogate to shortlist scenario candidates before mandatory exact verification.

## Supported modes

- `FLOOD`: administrator-defined `가정 침수영역` impact simulation; not physical flood prediction.
- `EARTHQUAKE`: administrator-controlled training geometry and road conditions; no collapse probability.
- `FIRE`: administrator-defined incident geometry and road avoidance; no building-fire spread model.
- `CIVIL_DEFENSE`: shelter capacity and emergency-water response context.
- `GENERAL_EVACUATION`: capacity-aware evacuation What-if.
- AED support keeps 119 as the first action.

## Final differentiators

1. 4D time-changing disaster state.
2. Capacity-aware evacuation assignment.
3. Road and facility outage propagation.
4. Affected-population and unserved-demand calculation.
5. Scenario A/B intervention comparison.
6. Response-resource context.
7. AI scenario triage with exact verification.
8. Public-data provenance and auditability.

The 90m DEM is not a release dependency and does not feed hazard geometry, routing, road closure, or facility safety inference. Citizen screens show official facility data and explicitly labeled training scenarios only.
