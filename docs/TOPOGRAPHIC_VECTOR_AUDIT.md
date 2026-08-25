# 2025 NGII 1:1,000 topographic-vector audit

Four user-supplied DXF packages were measured and preserved. All are current 2025 products, not raster DEMs.

| Sheet | DXF bytes | Entities | Layers | CRS | WGS84 footprint | AOI overlap |
|---|---:|---:|---:|---|---|---|
| 37612048 | 14,308,715 | 29,399 | 133 | EPSG:5186 | 126.925001–126.949999 E / 37.374881–37.400119 N | yes |
| 37612049 | 11,805,737 | 24,586 | 121 | EPSG:5186 | 126.950001–126.974999 E / 37.374886–37.400114 N | yes |
| 37612058 | 16,629,516 | 37,094 | 131 | EPSG:5186 | 126.925001–126.949999 E / 37.349881–37.375119 N | no |
| 37612059 | 12,918,122 | 27,442 | 111 | EPSG:5186 | 126.950001–126.974999 E / 37.349886–37.375114 N | no |

Every tile contains `LWPOLYLINE`, `TEXT`, and `INSERT` content. The measured elevation-support candidates are:

- `F0017111`: contour-like LWPOLYLINE entities with group-code-38 elevations;
- `F0017114`: index-contour-like LWPOLYLINE entities with group-code-38 elevations;
- `F0027217`: INSERT spot-elevation block instances with nonzero Z values.

The supplied ISO XML sidecars contain the 2025 production/survey dates, EPSG:5186, 1:5,000 metadata wording, DXF distribution format, and a `재배포 금지` restriction note. The XML is not well-formed enough for a strict XML parser, so the audit extracts evidence text without altering the source bytes.
