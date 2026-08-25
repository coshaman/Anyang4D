# Anyang DEM raster quality gate

The four ZIP files supplied under `docs/` were preserved byte-for-byte. Their SHA-256 is identical:

`40873ee25879aa52ee6665f534f0083d3ab7ca1c21bbaf5ad7aa7f3dff954598`

Each ZIP contains only `37612/37612.img`. The filenames therefore do not establish four distinct tiles; they are duplicate uploads of one package.

The HFA reader reports one `float32` band, 254 columns × 316 rows, native cell spacing **90 m × 90 m**, CRS `EPSG:5179`, origin `(933390, 1944720)`, bounds `(933390, 1916280, 956250, 1944720)`, nodata `-9999`, and elevation range `-4.5276` to `597.3775` m.

This is neither a native 1 m DEM nor a native 5 m DEM. A 5 m resampling would only create a denser grid; it would not create 5 m terrain information. The code and manifest keep `90 m` as canonical and label any 5 m grid as derived/display-only.

Evidence: [`anyang-dem-supplied-quality.json`](../artifacts/evals/data/anyang-dem-supplied-quality.json).

`GOAL3C_REAL_TERRAIN_GATE = false` for the requested high-resolution path. The supplied raster may support a clearly labeled coarse scenario preview, but it must not authorize high-resolution flood inference, water depth, route safety, or public routing changes.
