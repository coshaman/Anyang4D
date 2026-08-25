# High-resolution DEM final decision

## Final constants

```text
HIGH_RES_TERRAIN_ACQUISITION = CLOSED
STREET_LEVEL_FLOOD_TERRAIN_PATH = DROP
TERRAIN_DEPENDENCY_FOR_RELEASE = false
CITIZEN_HAZARD_ROUTING_FROM_TERRAIN = DROP
```

The NGII acquisition investigation is closed. The finest raster actually acquired for this project is a duplicate native 90m HFA product. The investigated official distribution path did not provide an obtainable post-2020 native 1m or 5m raster for this release. Historical metadata records are retained as research evidence only and do not imply downloadable current terrain.

This is a final product decision, not an unfinished feature. Terrain reconstruction and validation were performed; the predefined quality gates failed for street-level use. The result is validation-driven scope control.

The 90m product is not required by the release. If retained locally, it is `COARSE_TERRAIN_CONTEXT` only: broad geography or research/audit explanation. It is never used for flood calculation, water depth, probability, road safety, closure inference, building/shelter hazard, or routing. The public deployment excludes the raster.
