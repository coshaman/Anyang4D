# SAFE-Twin Anyang Goal 3D Terrain Validation Plan

Status: FROZEN before final reconstruction metrics

## Scope

This plan validates a computational terrain surface reconstructed from the 2025 NGII 1:1,000 topographic DXF tiles. It does not validate flood depth, hazard, evacuation, or citizen routing. The four source tiles are EPSG:5186; the demo AOI is covered directly by 37612048 and 37612049, with 37612058/37612059 retained as boundary context.

## Required evidence

The run must retain source SHA-256 hashes, sheet/layer/entity provenance, extracted constraint counts, contour interval evidence, support-density diagnostics, interpolation method and grid spacing, validation split definitions, seam diagnostics, road-corridor support, slope/sink/flow diagnostics, raster metadata, and the final terrain class.

## Frozen validation rules

Validation uses spatially grouped holdouts with a frozen 25 m projected-coordinate block: all training constraints in a held point/contour's block are removed. This prevents nearby contour vertices or spot points from leaking into training. Metrics are absolute elevation error in metres.

`TERRAIN_A` requires all of the following:

- grouped spot-height holdout MAE <= 2.0 m and P95 <= 5.0 m;
- withheld contour-segment P95 absolute deviation <= 2.5 m, or <= half the measured minimum supported contour interval when that interval is smaller;
- tile seam P95 absolute difference <= 2.0 m and median absolute difference <= 1.0 m;
- supported road-corridor P95 nearest-constraint distance <= 50 m;
- finite values, no unbounded spikes/sinks, valid coverage across the AOI, and slope P99 <= 1.5 (rise/run);
- no unresolved source/CRS/unit/provenance error.

`TERRAIN_B` requires all of the following, while failing at least one `TERRAIN_A` criterion:

- grouped spot-height holdout MAE <= 3.0 m and P95 <= 10.0 m;
- withheld contour-segment P95 absolute deviation <= 5.0 m;
- tile seam P95 absolute difference <= 5.0 m;
- supported road-corridor P95 nearest-constraint distance <= 100 m;
- finite values, valid coverage, slope P99 <= 2.0, and no unresolved source/CRS/unit/provenance error.

`TERRAIN_C` applies otherwise, including incomplete coverage, unresolved semantics, failed unit/CRS checks, non-finite output, or inability to produce reproducible validation evidence. `TERRAIN_C` output may be retained for diagnostics but must not be used to claim street-level hazard readiness.

## Diagnostic rules

- Report MAE, RMSE, median absolute error, P95, maximum absolute error, and sample counts for every holdout group.
- Report contour interval distribution and the exact threshold used for contour deviation.
- Report seam comparisons on both sides of each tile boundary, with sample count and percentile statistics.
- Report valid-cell coverage, min/max/P01/P99 elevation, slope percentiles, flat/negative/invalid cells, sink count, and flow-accumulation finiteness.
- Report road support separately for every edge/class and distinguish unsupported roads from supported roads; do not silently impute missing terrain.

## Authorization boundary

This artifact authorizes only derived terrain reconstruction and validation. It does not authorize flood simulation, hazard-frame production, evacuation routing, citizen routing, or public release of unsupported claims.
