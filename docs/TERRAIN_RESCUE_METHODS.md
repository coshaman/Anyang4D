# SAFE-Twin Anyang Goal 3D-R methods

Goal 3D-R is the final bounded terrain-rescue attempt. The original validation plan was hashed before new interpolation output: `72333c5a496c1f7abdf75ef567e22cea1c92d0944a7ae0103e6cdf830d808466`.

## Topology evidence

The actual 2025 DXF contours contain 700 polylines with constant elevation. Unique elevations are 25–200m at 5m intervals. There are 0 crossing pairs, 1,208 dangling endpoints, 96 closed contours, 0 duplicate geometries, 63 tile-boundary continuation pairs, and 0 vertical ordering anomalies. The dangling endpoints and spot elevations between contour levels are explicit warnings against treating the source as a complete closed-contour field.

## Method A — contour-aware distance

Implemented as `contour_aware_distance`: for each query, the nearest lower and upper distinct contour isolines are located using true point-to-polyline distance, then elevation is interpolated between the two isolines. Contour vertices are not treated as independent random observations. Exact holdouts use 25m spatial blocks and remove the held source contour from training.

Method A was run on a 10m diagnostic raster to bound runtime; point holdouts remain at exact source coordinates. Runtime was approximately 303.49s with approximately 209.17MB peak traced Python memory.

## Method B — RST

`METHOD_B_NOT_RUN`: GRASS/QGIS RST and a compatible spline backend were not available in the isolated environment. No unverified spline substitute was introduced and no final holdout was tuned against.

## Method C — constrained TIN

`METHOD_C_NOT_RUN`: no reliable constrained-TIN implementation was installed. Ordinary unconstrained triangulation would not preserve isoline breaklines, so it was not used merely to obtain a third row.

Full topology, method status, and comparable measurements are in `artifacts/evals/terrain/goal3dr/`.

