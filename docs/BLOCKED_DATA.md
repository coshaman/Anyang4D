# Blocked data and honest fallback status

This file is the current access/provenance boundary. A blocker is not treated as a downloaded dataset, and no fallback is silently promoted to official truth.

## Acquired and integrated

- Anyang municipal shelter context: 224 records, `ANYANG_LOCAL_OFFICIAL`; available through `/api/facilities?type=local_shelter` as a separate layer.
- National filtered civil-defense shelters: 231 records, `NATIONAL_OFFICIAL_FILTERED_ANYANG`; used as the operational shelter layer.
- Local emergency-water context: 46 records; national filtered emergency-water context: 71 records. Water capacity remains `RESPONSE_RESOURCE_CAPACITY`, not evacuation capacity.
- Flood-response inventory: 33 local records; dispatch optimization is not authorized.
- Anyang AED file: 305 records, with no source coordinates; AED remains address/context data and 119 is first.
- Official population: 31 administrative-dong units / 562,143 residents, reference date 2026-07-31. Spatial points are labeled simulated allocation anchors because the source has no dong polygons.
- Bounded OSM pedestrian graph and 2025 NGII topographic vectors are preserved with their source terms.

## Still blocked or insufficient

- Earthquake outdoor-shelter source: provider access flow requires human credential/application.
- Emergency medical institution API: provider access key/application required.
- Fire-water standard data: service key required.
- Current official emergency alerts, KMA weather, SGIS population grid, VWorld buildings, land cover and flood-trace raw layers: provider authentication or a public Anyang download is still unavailable.
- Latest official catalog recheck (2026-08-24): the NGII DEM 2024-09-24 catalog entry exists, but its actual IMG download is routed through the National Geographic Information Platform and requires login plus large-file-transfer software; catalog metadata alone is not raster acquisition.

## Closed research branch, not a release blocker

The high-resolution NGII DEM branch is permanently closed for this release. The supplied raster is native 90 m and remains `COARSE_TERRAIN_CONTEXT` provenance only; it is not a dependency for the product and cannot support flood depth, closure, routing, or safety inference. The processed terrain remains `TERRAIN_C`.

## Product boundary caused by the evidence

- `STREET_LEVEL_FLOOD_TERRAIN_PATH=DROP`
- `CITIZEN_HAZARD_ROUTING_FROM_TERRAIN=DROP`
- No quantitative water-depth claim or official emergency forecast is exposed.
- Admin hazard polygons are explicit `ADMIN_SCENARIO` What-If inputs; citizen training preview is not official guidance.

When a blocked provider becomes available, add its raw hash, terms, retrieval timestamp, CRS, quality report and Anyang count before connecting it to a solver or citizen surface.
