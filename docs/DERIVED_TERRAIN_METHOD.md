# Derived terrain method

Goal 3D uses a deterministic inverse-distance weighted surface over semantically extracted contour vertices and spot heights. The computational grid is 5 m; source constraint points are deterministically decimated to a 10 m spatial key for bounded computation. CRS is EPSG:5186 and output elevation units are metres.

The canonical artifact is `data/processed/terrain/anyang_demo_terrain.tif` with metadata in `artifacts/evals/terrain/goal3d/quality.json`. Provenance is `DERIVED_TERRAIN_FROM_TOPOGRAPHIC_VECTORS`. This method is a terrain diagnostic surface only; no flood engine consumes it in Goal 3D.

