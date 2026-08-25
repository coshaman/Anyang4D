# Goal 3C-RESET decision

## Current decision

- Current official vector source: **acquired and audited**.
- Historical 1 m DEM assumption: **deprecated**.
- 90 m IMG: **coarse official reference only; insufficient for street-level hazard**.
- Derived terrain: **not yet validated**.
- Real Anyang Level-A 4D field: **not yet eligible**.
- Admin-only 4D simulator: **may remain available only with explicit scenario/relative-hazard wording**.
- Citizen dynamic hazard routing: **not authorized**.

The reset materially improves terrain provenance because the new source is current 2025 NGII vector data. It does not permit skipping interpolation validation or treating a map-scale vector product as a 1 m DEM.

Evidence: [`TOPOGRAPHIC_VECTOR_AUDIT.md`](TOPOGRAPHIC_VECTOR_AUDIT.md) and [`anyang-topographic-vector-audit.json`](../artifacts/evals/data/anyang-topographic-vector-audit.json).
