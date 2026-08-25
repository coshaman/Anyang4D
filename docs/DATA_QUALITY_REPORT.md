# SAFE-Twin Anyang Goal 1 data quality report

Generated from `data/manifests/data_manifest.json` by `scripts/data/report_quality.py`.
All counts below are measured from raw bytes or the provider response; titles are not treated as evidence.

## Acquisition summary

- Manifest records: 15
- Downloaded or up-to-date: 5
- Human/provider access blockers: 10

## Measured datasets

### 전국민방위급수시설표준데이터 (안양 필터링)

- Status: `DOWNLOADED`
- Raw path: `data/raw/localdata/emergency_water/source.csv`
- Raw rows: 11030
- Rows containing 안양/Anyang: 83
- Encoding: `cp949`
- Coordinate columns: `{'latitude': None, 'longitude': None}`
- Valid WGS84 coordinate pairs: 0
- Projected coordinate columns: `{'x': '좌표정보(X)', 'y': '좌표정보(Y)'}`
- Valid projected pairs: 7776
- Numeric quality: `{'capacity': {'column': None, 'nonempty_count': 0, 'numeric_valid_count': 0, 'invalid_or_null_rate': 1.0}}`

### 전국민방위대피시설표준데이터

- Status: `DOWNLOADED`
- Raw path: `data/raw/localdata/civil_defense_shelter/source.csv`
- Raw rows: 18829
- Rows containing 안양/Anyang: 235
- Encoding: `cp949`
- Coordinate columns: `{'latitude': '위도(도)', 'longitude': '경도(도)'}`
- Valid WGS84 coordinate pairs: 18814
- Projected coordinate columns: `{'x': '좌표정보X(EPSG5179)', 'y': '좌표정보Y(EPSG5179)'}`
- Valid projected pairs: 18818
- Numeric quality: `{'capacity': {'column': '최대수용인원', 'nonempty_count': 18829, 'numeric_valid_count': 18829, 'invalid_or_null_rate': 0.0}}`

### OpenStreetMap 안양 보행 네트워크 bounded snapshot

- Status: `DOWNLOADED`
- Raw path: `data/raw/openstreetmap/anyang_pedestrian_broad/overpass.json`
- OSM elements: 136248
- Graph nodes: 108384
- Graph edges: 118092
- Connected components: 128
- Largest component fraction: 0.985321

### OpenStreetMap 안양 bounded demo pedestrian network

- Status: `DOWNLOADED`
- Raw path: `data/raw/openstreetmap/anyang_pedestrian_demo/overpass.json`
- OSM elements: 22134
- Graph nodes: 16745
- Graph edges: 19439
- Connected components: 27
- Largest component fraction: 0.981606

### 경기도 안양시 심폐소생 자동제세동기 정보

- Status: `DOWNLOADED`
- Raw path: `data/raw/data_go_kr/aed_anyang/source.csv`
- Raw rows: 305
- Rows containing 안양/Anyang: 305
- Encoding: `cp949`
- Coordinate columns: `{'latitude': None, 'longitude': None}`
- Valid WGS84 coordinate pairs: 0
- Projected coordinate columns: `{'x': None, 'y': None}`
- Valid projected pairs: 0
- Numeric quality: `{'capacity': {'column': None, 'nonempty_count': 0, 'numeric_valid_count': 0, 'invalid_or_null_rate': 1.0}}`

## Blockers

- `earthquake-outdoor-shelter`: official download endpoint returned HTTP 405 for GET and HTTP 415 for form POST; provider download flow requires its supported session/request; expected `SAFETYDATA_SERVICE_KEY`.
- `emergency-medical-institutions`: official portal documents an application-controlled linked service; no public file download was exposed in the page; expected `GYEONGGI_DATA_API_KEY`.
- `emergency-alerts`: official service is exposed through provider-controlled disaster-data access; no unauthenticated raw export was exposed; expected `SAFETYDATA_SERVICE_KEY`.
- `kma-weather`: actual request without ServiceKey returned HTTP 401 SERVICE_KEY_IS_NULL; expected `KMA_SERVICE_KEY`.
- `flood-traces`: no official Anyang raw vector download was exposed by the searched public catalogs; neighboring-city records are not an acceptable substitute; expected `FLOOD_TRACE_SOURCE_URL`.
- `gis-buildings`: actual request without key returned PARAM_REQUIRED: key; expected `VWORLD_API_KEY`.
- `sgis-population`: official authentication endpoint redirected to sgisapi.mods.go.kr and returned HTTP 412 for missing required parameters; expected `SGIS_SERVICE_KEY`.
- `environment-land-cover`: official service is a provider-controlled spatial service; no raw Anyang package was publicly exposed during acquisition; expected `EGIS_ACCESS_TOKEN`.
- `dem-terrain`: official high-resolution Korean DEM distribution is controlled by the national geospatial download service; no unauthenticated Anyang package was exposed; expected `NGII_ACCESS_TOKEN`.
- `fire-water-standard`: actual request returned HTTP 401 SERVICE_KEY_IS_NULL; expected `DATA_GO_KR_SERVICE_KEY`.

## Goal 3 flood viability

The currently acquired layers establish shelter/water/AED point coverage and a connected OSM pedestrian graph. They do not establish a flood model: Anyang flood traces, authoritative buildings, population grids, land cover, and DEM remain unavailable or access-gated. Proceeding to Goal 3 requires either the documented provider credentials or an explicit model-scope decision accepting those missing layers.
