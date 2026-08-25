# Goal 4A decision

Status: **IMPLEMENTED — ADMINISTRATIVE WHAT-IF ENGINE**.

Delivered: hazard-agnostic scenario contract, real 4D frame resolution, real OSM graph closure handling, official shelter-capacity constrained assignment, scenario A/B comparison, training-only route endpoint, provenance/audit storage, four labeled Anyang presets, and admin simulator UI.

Current data limits are explicit: national shelter (231 strict Anyang-address matches), national emergency-water (71 strict Anyang-address matches), AED (305), official Anyang administrative-dong population (31 units, total 562,143, source period 2026-07-31), and OSM are integrated. Local shelter/water crosswalk, earthquake shelters, fire-water, pump stations, and response inventory are not acquired. Population totals are official; spatial coordinates are `SIMULATED_SPATIAL_ALLOCATION` anchors and are not census-grid truth.

The admin layer exposes scenario JSON export with assumptions, frame metrics, source/provenance fields, affected roads, facility loads, resource state, and caveats. Resource events remain separate from evacuation capacity.

Terrain remains disabled for flood computation. Citizen emergency routing remains unchanged and does not consume admin scenario hazards. Training routes are labeled `훈련 시나리오 경로`.
