# Goal 3C-RESET — terrain source reset

The historical NGII DEM metadata remains `METADATA_ONLY`; it does not prove that a current downloadable 2009 1 m DEM exists. The four supplied 90 m IMG ZIPs remain rejected raw evidence and are classified `ANYANG_OFFICIAL_COARSE_REFERENCE` / `INSUFFICIENT_FOR_STREET_LEVEL_HAZARD`.

The valid current terrain source now present is four NGII 2025 1:1,000 digital topographic-map DXF packages with ISO sidecars. These are **topographic vectors, not a 1 m DEM**. Their declared CRS is EPSG:5186 and their sidecars identify 2025 production/survey dates and DXF format.

Current demo AOI: WGS84 bbox `(126.946, 37.376, 126.966, 37.396)`. Measured XML footprints show that only sheets `37612048` and `37612049` intersect this exact AOI; `37612058` and `37612059` are adjacent southern sheets and are retained as supplied context, not silently counted as AOI coverage.

The DXF audit found elevation-bearing contour polyline candidates (`F0017111`, `F0017114`) and spot-elevation block candidates (`F0027217`). Terrain derivation and validation remain separate from source acquisition and must retain provenance `DERIVED_TERRAIN_FROM_TOPOGRAPHIC_VECTORS`.

Evidence: [`anyang-topographic-vector-audit.json`](../artifacts/evals/data/anyang-topographic-vector-audit.json).
