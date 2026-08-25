# 2025 NGII DXF elevation-layer audit

The four user-supplied 2025 1:1,000 DXF sheets are current official vector source evidence in EPSG:5186. The demo AOI intersects 37612048 and 37612049; 37612058 and 37612059 provide adjacent context.

The extractor accepts only observed semantics: `F0017111`/`F0017114` LWPOLYLINE entities with constant group-code-38 elevation as contour constraints, and `F0027217` INSERT entities with group-code-30 elevation as spot-height constraints. Generic 3D Z values from other layers are rejected. Per-run counts and hashes are in `artifacts/evals/terrain/goal3d/quality.json`.

This is not a DEM. The surface is derived by explicit interpolation and remains subject to the frozen validation contract.

