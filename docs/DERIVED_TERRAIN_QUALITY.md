# Derived terrain quality

The frozen validation run classifies the current reconstruction as `TERRAIN_C`.

- Spot-height 25 m spatial-block holdout: MAE 6.35 m, RMSE 7.44 m, P95 13.07 m (100 samples).
- Contour 25 m spatial-block holdout: MAE 5.17 m, RMSE 5.33 m, P95 7.35 m (20 contour groups).
- Tile seam: median 3.27 m, P95 6.69 m (100 comparisons).
- OSM highway-way midpoint support: P50 25.33 m, P90 64.15 m, P95 77.99 m (1,294 sampled ways); worst sampled way 684968887 at 118.45 m.
- Candidate comparison: IDW power-2 was selected for the canonical continuous surface. Nearest-constraint achieved lower spot holdout error but was rejected as a discontinuity-prone pointwise overfit; both candidate metrics are retained in the quality artifact.
- Raster coverage: 100%; slope P99 0.6195; invalid cells 0; sink diagnostics 1,956.

The class is not a statement that the source data is invalid. It means this IDW reconstruction does not meet the pre-frozen street-level validation thresholds. It must not be used to claim flood depth, hazard, evacuation, or citizen-routing accuracy.
