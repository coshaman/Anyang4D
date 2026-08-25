# SAFE-Twin Anyang Goal 3D-R decision

Decision: **FINAL TERRAIN RESCUE FAILED — TERRAIN_C PERMANENTLY ACCEPTED**.

The contour-aware method improved spot-height error relative to the Goal 3D IDW baseline (spot MAE/RMSE/P95 `2.35/3.07/6.18m` vs `6.35/7.44/13.07m`) and improved seam median/P95 (`1.38/5.41m` vs `3.27/6.69m`). However, its contour holdout error worsened to MAE/RMSE/P95 `7.79/8.59/12.45m`, exceeding the frozen `TERRAIN_B` contour P95 limit of 5m. Road source support also remains approximately P50/P90/P95 `25.23/63.91/77.94m`; interpolation cannot create measurements where none exist.

No candidate passes the original frozen `TERRAIN_B` gate. No new canonical terrain is promoted. The prior 5m IDW artifact remains a failed diagnostic artifact only, not an operational substrate.

## Product boundary

- `STREET_LEVEL_FLOOD_TERRAIN_PATH = DROP`
- `CITIZEN_HAZARD_ROUTING_FROM_TERRAIN = DROP`
- `ADMIN_LEVEL_A_FLOOD_ELIGIBLE = false`
- `LEVEL_A_FLOOD_NEXT_GOAL_AUTHORIZED = false`
- `CITIZEN_ROAD_HAZARD_FUTURE_ELIGIBILITY = false`
- No further terrain-rescue attempt is authorized for this source branch.

## Recommended product architecture

Pivot away from street-level terrain-derived citizen guidance toward a separate 4D architecture based on official or administratively defined hazard polygons, time-dependent road closures, shelter capacity, population demand, evacuation flow, facility outages, and disaster-resource allocation. A coarse/admin scenario visualization may remain possible if independently justified, but it must not be presented as street-level terrain-derived guidance.

