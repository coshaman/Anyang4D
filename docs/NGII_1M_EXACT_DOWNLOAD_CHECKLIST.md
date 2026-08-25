# NGII 1 m exact download checklist — SAFE-Twin Anyang

Source metadata: `data/raw/ngii/dem_metadata_20231107.csv` (official NGII metadata snapshot; metadata only).

Official NGII web UI: https://map.ngii.go.kr/ms/map/NlipMap.do?tabGb=total

## Exact records to select

IMPORTANT: the local official metadata snapshot contains no 2020-or-newer record for any of the four target sheets. The 2009 records below are historical 1 m reference records only and do **not** satisfy the requested minimum year. Do not download them if the 2020+ requirement is mandatory.

The official NGII DEM dataset page is registered as a 2024 dataset and was modified in 2025, but the available per-sheet metadata CSV has no 2020+ production rows. The NGII UI must therefore be checked for a newer product directly.

### 안양048 / 37612048 — historical 1 m reference, **not 2020+ compliant**

- Grid interval: **exactly 1 m × 1 m** (`1m X 1m`)
- Production year: **2009**
- Data/product name: **수치표고자료**
- Format expected: **ASCII** (ASCII)
- CRS fields: **평면직각좌표계**, 지리좌표계 code `1`, origin `중부`
- Vertical datum: **인천항의 평균해수면**
- Accuracy: **0.25 m**
- Source/acquisition: `수치표고자료` / `항공레이저측량`
- Lower-left: `(X=193310, Y=430580)`
- Upper-right: `(X=195614, Y=433458)`
- UI distinguishing fields: `1m X 1m`, `2009`, `ASCII`, `평면직각좌표계`, `중부`, `인천항의 평균해수면`, `0.25 m`.

### 안양049 / 37612049 — historical 1 m reference, **not 2020+ compliant**

- Grid interval: **exactly 1 m × 1 m** (`1m X 1m`)
- Production year: **2009**
- Data/product name: **수치표고자료**
- Format expected: **ASCII** (ASCII)
- CRS fields: **평면직각좌표계**, 지리좌표계 code `1`, origin `중부`
- Vertical datum: **인천항의 평균해수면**
- Accuracy: **0.25 m**
- Source/acquisition: `수치표고자료` / `항공레이저측량`
- Lower-left: `(X=195523, Y=430578)`
- Upper-right: `(X=197828, Y=433456)`
- UI distinguishing fields: `1m X 1m`, `2009`, `ASCII`, `평면직각좌표계`, `중부`, `인천항의 평균해수면`, `0.25 m`.

### 안양058 / 37612058 — historical 1 m reference, **not 2020+ compliant**

- Grid interval: **exactly 1 m × 1 m** (`1m X 1m`)
- Production year: **2009**
- Data/product name: **수치표고자료**
- Format expected: **ASCII** (ASCII)
- CRS fields: **평면직각좌표계**, 지리좌표계 code `1`, origin `중부`
- Vertical datum: **인천항의 평균해수면**
- Accuracy: **0.25 m**
- Source/acquisition: `수치표고자료` / `항공레이저측량`
- Lower-left: `(X=193308, Y=427805)`
- Upper-right: `(X=195612, Y=430683)`
- UI distinguishing fields: `1m X 1m`, `2009`, `ASCII`, `평면직각좌표계`, `중부`, `인천항의 평균해수면`, `0.25 m`.

### 안양059 / 37612059 — historical 1 m reference, **not 2020+ compliant**

- Grid interval: **exactly 1 m × 1 m** (`1m X 1m`)
- Production year: **2009**
- Data/product name: **수치표고자료**
- Format expected: **ASCII** (ASCII)
- CRS fields: **평면직각좌표계**, 지리좌표계 code `1`, origin `중부`
- Vertical datum: **인천항의 평균해수면**
- Accuracy: **0.25 m**
- Source/acquisition: `수치표고자료` / `항공레이저측량`
- Lower-left: `(X=195522, Y=427803)`
- Upper-right: `(X=197826, Y=430682)`
- UI distinguishing fields: `1m X 1m`, `2009`, `ASCII`, `평면직각좌표계`, `중부`, `인천항의 평균해수면`, `0.25 m`.

## 2020+ selection rule for the NGII UI

For each of the four sheet numbers above, select a record whose UI production/build year is **2020 or newer**, while retaining the following as cross-checks: native `1m X 1m`, `ASCII`, the sheet number, sheet-specific extent, explicit CRS, explicit vertical datum, and accuracy. If the UI shows only the 2009/2006 records documented here, stop; that is a HUMAN_ACTION_REQUIRED condition, not a successful 2020+ acquisition.

## Reject the wrong product immediately

After each download, do not assume success from the filename. Inspect the raster before adding it to `data/raw/ngii/` and reject it if:

- X/Y pixel spacing is not approximately 1 m;
- all four files have identical SHA-256;
- raster dimensions/extents indicate one regional 90 m product;
- CRS or extent does not match that sheet.

The previously supplied files fail this test: all four have SHA-256 `40873ee25879aa52ee6665f534f0083d3ab7ca1c21bbaf5ad7aa7f3dff954598`, native 90 m spacing, and identical `254×316` EPSG:5179 HFA content. The exact catalog product cannot be identified from the local metadata CSV; it is not one of the target 1 m records.

## HUMAN_ACTION_REQUIRED

Open the official NGII download page: https://map.ngii.go.kr/ms/map/NlipMap.do?tabGb=total

Download exactly one native 1 m ASCII product for each target sheet only after the UI exposes a production/build year of 2020 or newer, preserving the NGII-provided filename and any sidecar metadata. If no 2020+ record is exposed, do not substitute the 2009/2006 record. Do not download a 10 m or 90 m record for Goal 3C. Login and the NGII large-file transfer workflow may be required.

Evidence JSON: `artifacts/evals/data/ngii-target-1m-records.json`.
