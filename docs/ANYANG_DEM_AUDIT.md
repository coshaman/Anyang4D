# Goal 3A — Anyang DEM metadata audit

Audit date: 2026-08-21

The official NGII metadata CSV is preserved at `data/raw/ngii/dem_metadata_20231107.csv`.
It is metadata, not raster elevation bytes. SHA-256: `10e46e3c749e91c4aa6a9de41dff1d724b09dd355cd9c90e63c7f4181e62fe3e`.

The file contains 23,190 rows. Filtering `도엽명5000` for `안양` yields 359 records and 101 distinct sheet names: `안양001`–`안양100` plus the separately written `안양2`. The recorded grid intervals are:

| Recorded interval | Records | Production years | Interpretation |
| --- | ---: | --- | --- |
| 1 m | 158 | 2006, 2007, 2009 | Best recorded resolution; heterogeneous legacy products |
| 10 m | 200 | 2001, 2002 | Coarser legacy products |
| 90 m | 1 | 2014 | Coarsest outlier; not suitable for a local hazard field |

The 1 m records are ASCII products. The 2009 records report `평면직각좌표계`, vertical datum `인천항의 평균해수면`, and 0.25 m accuracy; the 2007 records report `세계측지계`, the same vertical datum, and 0.27 m accuracy. The 2006 records are present in the metadata but must not be treated as interchangeable without checking their individual CRS and coverage.

This establishes “best recorded metadata resolution = 1 m”; it does not establish that a current 1 m raster is downloaded, complete, or spatially aligned with the simulator. The raster-access audit is `HUMAN_AUTH_REQUIRED` / metadata-only: the official DEM distribution page directs users through the NGII platform and states that login and large-file transfer software are required.

Sources: [NGII aerial-photo/DEM metadata](https://www.data.go.kr/data/15067637/fileData.do) and [NGII DEM distribution record](https://www.data.go.kr/data/15059920/fileData.do). Machine-readable evidence: `artifacts/evals/data/anyang-dem-audit.json`.
