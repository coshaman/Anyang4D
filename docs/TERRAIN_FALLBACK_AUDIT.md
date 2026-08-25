# Terrain fallback audit

| Candidate | Resolution / type | Access and license | Anyang coverage | Decision |
| --- | --- | --- | --- | --- |
| NGII 2009 records | 1 m metadata target; raster gated | Official NGII distribution; human login/download action | Confirmed by metadata | Preferred real input; `HUMAN_ACTION_REQUIRED` |
| Copernicus DEM GLO-30 | 30 m DSM | Free license with attribution; registered access may apply | Global | Auxiliary/smoke-test only; rejected for street-level flood behavior |
| Copernicus DEM GLO-90 | 90 m DSM | Free/open terms with attribution | Global | Rejected for local urban flood behavior; plumbing only |
| NASA SRTM 1 arc-second | Approximately 30 m elevation sampling | Public NASA data distribution | Covers Anyang latitude | Auxiliary/smoke-test only; rejected as an NGII replacement |

The fallbacks are not secretly substituted for the NGII 1 m target. They may support contract, reprojection, and performance tests under `AUXILIARY` or `BENCHMARK` provenance, never `ANYANG_OFFICIAL` street-level flood output. Copernicus describes GLO-30/GLO-90 as global DEM products with free licensing, while NASA documents SRTM’s approximately 30 m sampling; neither has the urban micro-topography required for the intended Level-A demo.

Sources: [Copernicus DEM](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM), [Copernicus DEM technical access](https://copernicus-dem-30m.s3.amazonaws.com/readme.html), and [NASA SRTM](https://data.nasa.gov/dataset/shuttle-radar-topography-mission-srtm-images).
