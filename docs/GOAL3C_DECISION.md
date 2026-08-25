# SAFE-Twin Anyang Goal 3C decision

## Decision

`GOAL3C_REAL_TERRAIN_GATE = false`

`GOAL4_AUTHORIZED = false`

The supplied files do not satisfy the requested real high-resolution terrain gate. This is a data-quality decision, not an AI-engine decision.

## Evidence

- Four ZIPs were found in `docs/` and preserved unchanged.
- All four have the same SHA-256: `40873ee25879aa52ee6665f534f0083d3ab7ca1c21bbaf5ad7aa7f3dff954598`.
- Each contains the same single `37612/37612.img` file.
- Raster driver: ERDAS HFA; dimensions `254×316`; one `float32` band.
- Native resolution: `90 m × 90 m`; CRS: `EPSG:5179`; nodata: `-9999`.
- Therefore these are not four distinct 1 m or 5 m tiles.

## Safety boundary

The implementation keeps the canonical source at 90 m. A future 5 m resampling may be used only as a labeled derived/display grid; it must not be called a 5 m DEM or interpreted as newly observed terrain detail. No water depth, official forecast, route safety, or public routing change is authorized from this upload.

## Required next action

Provide four distinct NGII Anyang tiles at native 1 m or 5 m resolution, or explicitly approve a coarse 90 m scenario-only preview. The supplied files alone are insufficient for the requested Goal 3C high-resolution 4D field.

Quality evidence: [`anyang-dem-supplied-quality.json`](../artifacts/evals/data/anyang-dem-supplied-quality.json).
