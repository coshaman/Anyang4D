# SAFE-Twin Anyang progress

## Goal 0 — foundation

Status: implemented and verified for Goal 0 foundation.

### Changed files

- Added Vite/React/TypeScript web foundation and FastAPI contract service.
- Added explicit provenance contracts and fixture-only facility response.
- Added responsive map-first citizen shell, large-text mode, Korean safety copy, and admin entry point.
- Added anti-slop and secret checks, data directories, manifest, notices, and this evidence log.

### Commands and evidence

Commands actually run:

- `npm install` — passed; 117 packages audited, 0 vulnerabilities.
- `npm test -- --pool=threads --poolOptions.threads.singleThread` — passed, 1 file / 2 tests.
- `npm run build` — passed; Vite production bundle generated in `dist/`.
- `python -m pytest tests/test_api_contract.py -q` — passed, 2 tests.
- `python -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000` — server started; `GET /api/foundation` returned HTTP 200 with all four provenance values and `fixture: true`.
- `npm run test:e2e` — passed, 4 tests across 390×844 phone and desktop projects.
- `npm run test:e2e` — passed, 6 tests across 390×844 phone and desktop projects, including axe checks with no serious/critical violations.
- `python scripts/check_anti_slop.py` — passed.
- `python scripts/check_secrets.py` — passed.

Screenshots inspected:

- `artifacts/screenshots/foundation-phone.png` — 390×844 responsive map-first layout.
- `artifacts/screenshots/foundation-desktop-admin.png` — desktop map-first layout.

No live public dataset or model is integrated in Goal 0.

### Unvalidated assumptions / blockers

- Goal 0's historical note mentions the base Python; Goal 1 corrected the project boundary with `.venv` and verified the data-audit tests there. Future Python commands must use `.venv\Scripts\python.exe`.
- Fixture map is intentionally not a real map and must not be presented as current public data.
- Accessibility screenshots and axe checks require the Playwright/browser runtime.

## Goal 1 — public data acquisition and audit

Status: acquisition and evidence audit implemented. Models and Goal 2 were not started.

### Environment

- Created project-local `.venv` with Python 3.12.13.
- Declared runtime and dev dependencies in `pyproject.toml`; generated `requirements.lock.txt` from the project environment.
- `\.venv\Scripts\python.exe -m pytest tests/test_data_audit.py -q` — passed, 5 tests.

### Downloaded raw bytes

- Civil-defense shelters: `data/raw/localdata/civil_defense_shelter/source.csv`, SHA256 `812dff739538dbe44db0f096678f2c962ef4109c0c1bdd8b5363fc3b73e52dcb`; 18,829 raw rows, 235 Anyang rows, 18,814 valid WGS84 pairs.
- Emergency water: `data/raw/localdata/emergency_water/source.csv`, SHA256 `92bb644e8874c9730eacc92d0266803ec62d087796f17c580dcc19954722425f`; 11,030 raw rows, 83 Anyang rows, 7,776 valid projected pairs.
- Anyang AED file: `data/raw/data_go_kr/aed_anyang/source.csv`, SHA256 `642ba890dbcab650e361d64c0a18e73e366f3bb785e0ad81161c89c1ab0cf672`; 305 rows. The provider file has no coordinate columns.
- OpenStreetMap Overpass bounded snapshot: 136,248 elements, 108,384 graph nodes, 118,092 edges, largest component fraction 0.985321; ODbL attribution recorded.

### Reproducible audit artifacts

- `data/manifests/data_manifest.json` contains all 14 required-source statuses, raw paths, hashes, CRS/temporal notes, and blocker evidence.
- `scripts/data/fetch_sources.py`, `scripts/data/fetch_osm.py`, `scripts/data/audit_csv.py`, `scripts/data/audit_osm.py`, and `scripts/data/report_quality.py` provide repeatable acquisition and inspection.
- `docs/DATA_QUALITY_REPORT.md` and `artifacts/evals/data/` contain measured schema/count/coordinate/graph evidence and the Goal 3 flood viability decision.
- `docs/BLOCKED_DATA.md` records all genuine access-gated or unavailable sources. No source title was treated as proof of contents.

## Goal 2 — real-data spatial twin and citizen baseline

Status: implemented and verified; Goal 3 model work intentionally not started.

### Delivered

- Reproducible processed artifact: `data/processed/anyang_facilities.json`, generated from the Goal 1 manifest and raw bytes with 235 shelters, 83 emergency-water facilities, and 305 AED records.
- Truthful normalization: shelter capacity/operating fields remain unknown when absent; water EPSG:5174 X/Y is converted to WGS84; AED records retain missing coordinates and are never plotted as invented points.
- Real MapLibre + OpenStreetMap raster map with attribution, facility selection/details, category filtering, search, AED-first 119 flow, geolocation denial fallback, and basic OSM walking route endpoint.
- API contracts expose official provenance, source availability, counts, route geometry/distance, and explicit null hazard/closure fields. Blocked Goal 1 sources are not represented as facilities.
- Offline foundation: installable web manifest and same-origin app-shell service worker. OSM tiles and dynamic APIs are deliberately not cached or fabricated offline.
- Citizen `/about-data`, simulation preview shell, admin spatial shell, large-text mode, keyboard-visible controls, responsive layouts, and accessibility checks.

### Verification evidence

- `\.venv\Scripts\python.exe -m pytest -q` — passed, 16 tests.
- `npm test -- --pool=threads --poolOptions.threads.singleThread` — passed, 4 tests.
- `npm run build` — passed.
- `npm run check:anti-slop` — passed.
- `npm run check:secrets` — passed.
- `npx playwright test tests/e2e/goal2.spec.ts --workers=1` — all 8 cases reported `ok` across phone and desktop projects, including serious/critical axe checks, AED, geolocation denial, offline, simulation preview, required viewport screenshots, and 200% zoom.

Screenshots: `artifacts/evals/ui/goal2-*.png`; visual notes: `artifacts/evals/ui/goal2-visual-review.md`.

### Explicit limits carried forward

- OSM is a retrieval snapshot, not an authoritative hazard, closure, or time-dependent routing source; route responses keep those fields null.
- AED source has no coordinates; the citizen UI provides the 119-first flow and text list without false map points.
- Simulation is a preview shell only. No Goal 3 hazard model, prediction, risk score, or evacuation simulation was implemented.

## Goal 3A — flood-model path, license, and maturity decision

Status: audited and decisioned; flood outputs are not integrated.

### Evidence delivered

- Downloaded official NGII DEM metadata CSV: 23,190 rows; 359 Anyang-named records; 101 sheet names; recorded intervals 1 m (158), 10 m (200), and 90 m (1). The file is metadata-only; raster access remains `HUMAN_AUTH_REQUIRED` pending NGII portal login and large-file transfer.
- Added `scripts/data/dem_metadata.py`, `scripts/data/audit_dem.py`, `artifacts/evals/data/anyang-dem-audit.json`, and `docs/ANYANG_DEM_AUDIT.md`.
- Added explicit license, maturity, and provenance gates in `scripts/model_audit.py` with tests.
- Audited PhysicsNeMo (Apache-2.0), EPA SWMM (Public Domain), PySWMM (BSD-2-Clause), and LarNO (source HOLD pending authoritative license-file archive; model/dataset benchmark-only conditional).
- Added fail-closed PhysicsNeMo and SWMM environment probes. Current environment has no PyTorch, PhysicsNeMo, SWMM executable, or PySWMM; no synthetic or Anyang flood result was produced.
- Added `docs/FLOOD_FIDELITY_REQUIREMENTS.md`, `docs/FLOOD_MODEL_LICENSE_AUDIT.md`, `docs/GOAL3_REQUIRED_HUMAN_ACTIONS.md`, `docs/GOAL3A_DECISION.md`, model cards, and `THIRD_PARTY_NOTICES.md`.

### Verification

- `\.venv\Scripts\python.exe -m pytest -q` — passed, 24 tests.
- `\.venv\Scripts\python.exe scripts\data\audit_dem.py ...` — passed; 23,190 raw rows, 359 Anyang records, 101 sheets, best recorded interval 1.0 m.
- PhysicsNeMo probe — `BLOCKED_ENVIRONMENT`; SWMM probe — `BLOCKED_ENVIRONMENT`.

### Decision boundary

Goal 3B may pursue a SAFE-Twin-owned Level A relative scenario-hazard path after human acquisition of aligned DEM and rainfall. Level B requires Anyang flood labels. Level C quantitative depth is deferred until drainage topology and calibration observations exist. LarNO is not vendored; SWMM is reserved as a future teacher; Goal 4 routing remains untouched.

## Goal 3B — operational flood-engine preparation

Status: deterministic Level-A engine, provenance-gated contract, 4D frame storage/API, internal synthetic lab, AOI selection, and evidence documentation implemented. Real Anyang flood output is not integrated; Goal 4 is not authorized.

### Delivered

- Hardware evidence: `artifacts/evals/ml/goal3b-hardware.json`.
- Isolated PhysicsNeMo attempt: `.venv-physicsnemo`; native CPU pip path stalled twice during torch installation; exact evidence in `artifacts/evals/ml/physicsnemo/environment.json`. No PhysicsNeMo runtime dependency was added.
- Contract/gate: `services/flood/contracts.py`; `WATER_DEPTH_M` is rejected below Level C or for synthetic/benchmark provenance.
- Deterministic engine: `services/flood/baseline.py`; synthetic tests cover lower terrain, rainfall monotonicity, nodata, and alignment.
- 4D storage/API: `services/flood/storage.py`, `services/api/simulation.py`, `/api/internal/simulations/*`; citizen `/api/routes` remains unchanged.
- Synthetic evaluation: `artifacts/evals/ml/goal3b/{config.json,metrics.json,synthetic-target.npz}`.
- AOI and exact four-sheet request: `docs/DEMO_AOI.md`, `docs/NGII_DEM_DOWNLOAD_REQUEST.md`, `artifacts/evals/data/demo-aoi.geojson`.
- Terrain fallback audit and safety/model documentation completed.

### Explicit limits

- Current generated fields are `SYNTHETIC` relative hazard, not water depth and not Anyang truth.
- Level B/C remain blocked by missing Anyang observations, drainage/inlet/sewer topology, and calibration evidence.
- The internal lab is visibly marked `합성 테스트 시나리오`; no citizen route consumes it.

## Goal 3C-RESET — current topographic-vector path

Status: current vector source acquired and audited; derived terrain and real Anyang Level-A remain pending validation.

- Added four user-supplied NGII 2025 1:1,000 DXF packages plus XML/XLSX sidecars to provenance review.
- Added `scripts/data/audit_anyang_topographic_vectors.py` and `artifacts/evals/data/anyang-topographic-vector-audit.json`.
- Measured official EPSG:5186 DXF content with contour candidates (`F0017111`, `F0017114`) and spot-elevation candidates (`F0027217`).
- Exact current AOI intersects sheets `37612048` and `37612049`; `37612058` and `37612059` are adjacent southern context tiles.
- Deprecated historical 1 m DEM assumption; 90 m IMG remains coarse-reference evidence only.
- Added RESET documents covering terrain provenance, vector audit, derived quality gates, local-data crosswalk, licenses, and blockers.
- No flood simulation or PhysicsNeMo work was run in RESET.
## Goal 3D — 2025 NGII topographic-vector terrain reconstruction (2026-08-22)

- Frozen validation contract: `docs/TERRAIN_VALIDATION_PLAN.md`.
- Parsed four 2025 EPSG:5186 DXF sheets with source hashes and provenance; main AOI coverage is 37612048/37612049, with 37612058/37612059 as context.
- Extracted only observed contour/spot semantics (`F0017111`, `F0017114`, `F0027217`); generic 3D layers are rejected.
- Built reproducible 5 m IDW computational terrain from 10 m deterministic constraint decimation and wrote `data/processed/terrain/anyang_demo_terrain.tif`.
- Validation evidence: 25m grouped spot MAE/RMSE/P95 6.35/7.44/13.07 m; contour MAE/RMSE/P95 5.17/5.33/7.35 m; seam median/P95 3.27/6.69 m; road support P50/P90/P95 25.33/64.15/77.99 m, worst way 684968887 at 118.45m; coverage 100%; slope P99 0.6195; sink count 1,956.
- Candidate comparison: IDW power-2 selected as the continuous surface; nearest-constraint had lower sparse spot error but was rejected as discontinuity-prone pointwise overfit. Candidate metrics are in `artifacts/evals/terrain/goal3d/quality.json`.
- Decision: `TERRAIN_C` diagnostic-only. Flood simulation, hazard frames, Goal 4 routing, citizen routing, and PhysicsNeMo were not run or authorized.
- Existing absent-governance-doc condition remains recorded: `AGENTS.md`, `docs/PRODUCT_SPEC.md`, `docs/SAFETY_AND_CLAIMS.md`, and `docs/ARCHITECTURE.md` were not present; existing RESET/decision/quality docs were used instead.
- Verification: `.venv\\Scripts\\python.exe -m pytest -q` => 50 passed; canonical GeoTIFF reopened as 445x355 EPSG:5186; `python scripts/check_anti_slop.py` and `python scripts/check_secrets.py` passed; `npm run build` passed. The default system Python collection failure due to missing pre-existing `pyproj`/`requests` was not used as the Goal 3D verification runtime.
- Goal 3D-R final rescue completed: frozen validation plan hash `72333c5a496c1f7abdf75ef567e22cea1c92d0944a7ae0103e6cdf830d808466`; contour topology 700 polylines, 5m interval, 0 crossings, 1,208 dangling endpoints, 96 closed, 0 duplicates, 63 tile continuations.
- Contour-aware Method A improved spot MAE/RMSE/P95 to 2.35/3.07/6.18m and seam median/P95 to 1.38/5.41m, but contour MAE/RMSE/P95 worsened to 7.79/8.59/12.45m; final class remains `TERRAIN_C`.
- Method B RST: `METHOD_B_NOT_RUN` because no GRASS/QGIS/spline backend was available. Method C constrained TIN: `METHOD_C_NOT_RUN` because no reliable constrained implementation was installed.
- Rescue decision: no canonical promotion; `STREET_LEVEL_FLOOD_TERRAIN_PATH=DROP`, `CITIZEN_HAZARD_ROUTING_FROM_TERRAIN=DROP`, and no further terrain rescue. See `docs/GOAL3D_RESCUE_DECISION.md`.

## Goal 4A — administrative multi-hazard 4D what-if engine (2026-08-22)

Status: implemented with explicit administrative/training-only boundaries.

- Added hazard-agnostic scenario contracts, stepwise hazard keyframes, dynamic road closures, facility availability/capacity state, demand/resource provenance, deterministic capacity-constrained assignment, A/B comparison, and training-only routes.
- Added four Anyang presets: flood-style administrative exercise, earthquake training, fire exclusion training, and civil-defense outage. These are hypothetical `ADMIN_SCENARIO` states; no terrain flood depth or citizen guidance is connected.
- Integrated 231 strictly address-filtered national civil-defense shelters, 71 national emergency-water context records, and the bounded OSM demonstration graph. Four shelter and twelve water rows matched only a broad 안양 substring and were excluded; the filter audit is `artifacts/evals/data/goal4a-facility-filter-audit.json`. Emergency-water capacity remains unknown and is not inferred.
- Acquired and integrated the official 안양시 2026-07-31 resident population workbook: 31 administrative-dong demand units totaling 562,143 residents. Coordinates are explicitly simulated allocation anchors because dong polygons are not in the source.
- Added scenario store/audit log, source audit, shelter crosswalk artifact, resource model, four-dimensional state model, assignment model, and `docs/GOAL4A_DECISION.md`.
- Goal 4A verification: `.venv\\Scripts\\python.exe -m pytest -q` => 73 passed; `npm test -- --pool=threads --poolOptions.threads.singleThread` => 5 passed; `npm run build`, anti-slop, and secret checks passed. Direct Playwright desktop shell/phone/axe run => 2 passed; authoring/timeline/A-B/export/reduced-motion/visual matrix => 1 passed. Runtime benchmark on the bounded OSM demo AOI: median 5,949.77 ms, max 7,002.0 ms/frame; this is evidence, not a whole-city real-time SLA. Visual review: `artifacts/evals/ui/goal4a-visual-review.md`.

## Goal 5A — administrative AI surrogate screening (2026-08-22)

Status: implemented and validated as `AI_SURROGATE_B`; `ADMIN_AI_SCENARIO_SCREENING=DEMO_ONLY`.

- Added reproducible 160-row simulated administrative scenario corpus with source hashes, pre-solver feature extraction, exact Goal 4B reference labels, grouped train/validation/test split, held-out OOD families, median/Ridge/HistGradientBoosting baselines, official-population/capacity/graph-disruption ablations, model card, and versioned CPU model bundle.
- Added `/api/admin/goal5a/screen`, `/verify/{scenario_id}`, and `/status`. AI output is explicitly non-authoritative; exact Goal 4B verification is required for the displayed shortlist and citizen guidance remains unauthorized.
- Validation ranking: Ridge Spearman 0.977020, Recall@20 0.95, NDCG@20 0.997453. OOD ranking: Spearman 0.964430, Recall@20 0.85. Assignment-cost P95 error remains high, so this is not an operational primary verifier.
- Exact label generation: 160 scenarios, 256,965.413 ms total, 11,121.862 ms maximum single scenario. Runtime benchmark: 20 scenarios, AI+exact top-5 measured 1.982x faster than exact-all, avoiding 15 exact calls.
- Added admin demo-only AI shortlist panel with separate AI estimate/exact values and a Playwright mock-backed separation test.
- Verification: Goal5A targeted pytest 9 passed; real HTTP screen smoke passed with 2 candidates/1 exact call; Goal4A+Goal5A AI UI E2E 2 passed; the subsequent Goal6A release gate adds full Python/Vitest/build/audit verification and real-browser capture.

## Goal 6A — competition release hardening (2026-08-24)

Status: `COMPETITION_RELEASE_B`; feature development frozen.

- Added release readiness endpoint `/api/release/readiness`, deterministic `scripts/start_demo.ps1`, and real HTTP `scripts/smoke_demo.ps1`.
- Added single-source claims matrix, data consistency artifact, AI reproducibility artifact, release data policy, technical evidence, one-page summary, release audit, fixed A/B preset, and visual review.
- Data consistency measured: local shelters 224, national filtered shelters 231, local water 46, national water 71, response inventory 33, AED 305, population 31 units / 562,143 people.
- AI scale measured on CPU at N=20/100/160/500 with actual candidate generation, feature extraction, inference, and exact top-5 verification. N=1000 was explicitly not extrapolated because feature extraction exceeded a practical benchmark window.
- Real browser demo capture produced seven screenshots. Latest warm route load was 1,466 ms; conservative representative 100-candidate AI+exact timing is 24,889 ms; cold start workflow measured 15,380 ms. OSM tile failure behavior retained a usable neutral map/data layout.
- Final verification: Python 91 passed; Vitest 5 passed; Playwright 18 passed; production build passed; anti-slop, secrets, Goal 4B boundary, Goal 5A claims, Goal 6A release audits passed. No Goal 6B started.

## Goal 6B — submission evidence and content master (2026-08-24)

Status: `SUBMISSION_CONTENT_READY = true`; product remains frozen at `COMPETITION_RELEASE_B`.

- Reconciled the stale 23.401 s one-page value against the final browser artifact. The authoritative conservative representative 100-candidate AI+exact timing is 24.889 s; latest warm repetition 12.408 s is labeled separately.
- Corrected the stale shelter crosswalk wording and fixed the authority at local 224 / national 231 with 24 exact, 147 strong, 53 local-only, 60 national-only, and 0 ambiguous relationships.
- Added the 10-page content master, figure plan, scoring map, human checklist, package manifest, judge Q&A, 3-minute demo script, Goal 6B decision, evidence consistency artifact, and claim audit.
- Selected seven real browser screenshots for submission evidence. Raw NGII DXF/DEM remains excluded from the public package under the release policy; no official HWPX/PDF was modified.

## ZIP implementation continuation — citizen training preview (2026-08-24)

Status: implemented on top of the frozen `COMPETITION_RELEASE_B` boundary.

- Confirmed the user ZIP is already extracted at `SAFE-Twin_Anyang_Codex_Pack/` and re-read its working contract, product spec, safety policy, architecture, design system, data/license rules, and goal plan.
- Replaced the citizen `/simulate` placeholder with a real, simplified training preview backed by `/api/admin/goal4a/scenarios` and exact frame responses. It shows scenario time, hazard provenance, changed roads, available shelters, evacuation demand, assigned/unserved counts, and explicitly states that it is not an official instruction or safety guarantee.
- Reused the existing exact simulator and `MapView`; no terrain-derived citizen routing, flood-depth claim, or official hazard claim was added. `terrain_authorized=false` and `citizen_guidance_authorized=false` remain visible in the backend frame contract.
- Added responsive training-result styling and updated the citizen unit/E2E acceptance tests.
- Verification: targeted Vitest 5 passed; full production build passed; anti-slop passed; secrets passed; real API scenario/frame probe returned `CACHED`, `terrain=false`, `citizen=false`; full Playwright with 2 workers passed 18 tests.
- A 6-worker browser run exposed backend contention under concurrent CPU-heavy frame requests; the affected tests pass standalone and under the stable 2-worker release command.
- Added `GET /api/facilities?type=local_shelter` as a separate official municipal context layer. It returns 224 local records with `ANYANG_LOCAL_OFFICIAL` provenance and never merges them into the 231-record national operational list. Real HTTP verification after the exact demo backend restart returned `OFFICIAL`, count `224`; full Python suite: 92 passed, 40 warnings.
- Reconciled the stale `docs/BLOCKED_DATA.md` counts/status with the current manifest. Remaining provider-auth items are provenance limits; the 90 m DEM branch is now explicitly closed and not a release blocker. Release audit and Vitest remained passing after the documentation correction.

## Goal 6 — explicit multi-hazard mode contracts (2026-08-24)

- Added `GET /api/admin/modes` and `GET /api/admin/modes/{mode}` as a machine-readable contract for FLOOD, EARTHQUAKE, FIRE, CIVIL_DEFENSE, and AED.
- Each mode now declares source status, supported calculations, unsupported claims, and whether citizen guidance is authorized. The admin scenario editor reads this contract before saving a new mode.
- This makes provider gaps visible without fabricating earthquake, fire-water, medical, alert, or terrain-flood data. `FLOOD` remains `ADMIN_SCENARIO`; it does not expose terrain-derived flood depth or a citizen safe route.
- Verification: `\.venv\Scripts\python.exe -m pytest -q tests/test_modes_api.py` passed 2 tests; `npm run build` passed.

## Goal 7 — optional AI module decision (2026-08-24)

- Added `GET /api/admin/optional-modules` and detail routes for TerraMind, xBD-S12, MapAnything, and JuPedSim.
- All four are explicitly `REJECTED` for this release because the repository has no legally sourced EO/photo inputs, manual measurements, local labels, or calibration observations required for defensible evaluation.
- Added `docs/GOAL7_DECISION.md`; no optional model is installed or exposed as an operational predictor. Future outputs remain admin-review-only (`OBSERVED_AI` or `SIMULATED_ADMIN_SCENARIO`) until evidence gates pass.
- Verification: `\.venv\Scripts\python.exe -m pytest -q tests/test_optional_modules_api.py` passed 2 tests.
- Runtime verification after exact backend restart: `/api/admin/optional-modules` returned 4 items, all `REJECTED`.

## Goal 3 — runtime terrain gate made explicit (2026-08-24)

- Added admin-only `GET /api/admin/flood-readiness`, backed by `artifacts/evals/data/anyang-dem-supplied-quality.json`.
- It returns `NO_GO_REAL_TERRAIN`, native `90m`, duplicate-source evidence, `TERRAIN_C`, and the exact authorization split: admin What-if remains allowed; real terrain Level-A and citizen routing remain disabled.
- This endpoint prevents the 90m input or a derived display grid from being misrepresented as the requested 1m/5m DEM.
- Verification: `tests/test_flood_readiness_api.py` passed.
- External recheck: the official 2024-09-24 DEM catalog is metadata-only for this workspace; its download flow requires National Geographic Information Platform login and large-file-transfer software. Manifest and `BLOCKED_DATA.md` now retain this retrieval evidence.
- Corrected `docs/NGII_DEM_DOWNLOAD_REQUEST.md` so its operative request is 2020+ native 1m/5m; the historical 2009 records are explicitly reference-only.

## ZIP objective audit — historical pre-pivot snapshot (2026-08-24)

- Added `scripts/evals/audit_zip_objective.py` and `services/release/zip_audit.py`.
- The generated `artifacts/evals/release/zip-objective-audit.json` separates locally implemented goals from external gates instead of treating a green UI test as proof of real terrain readiness.
- Historical result before FINAL-PIVOT: `IMPLEMENTED_WITH_EXTERNAL_GATES`. Superseded by the final decision below; the terrain/rainfall branches are now closed research branches and are not release dependencies.

## FINAL-PIVOT-AND-RELEASE — final release boundary (2026-08-24)

Status: `FINAL_RELEASE_B`; feature development frozen. The previous high-resolution DEM research branch is permanently closed as a release dependency. `HIGH_RES_TERRAIN_ACQUISITION=CLOSED`, `TERRAIN_DEPENDENCY_FOR_RELEASE=false`, `STREET_LEVEL_FLOOD_TERRAIN_PATH=DROP`, and `CITIZEN_HAZARD_ROUTING_FROM_TERRAIN=DROP` are now reflected in the manifest, readiness payload, product scope, claims matrix, and final decision.

- Product scope is the validated 4D administrative multi-hazard What-if core: FLOOD, EARTHQUAKE, FIRE, CIVIL_DEFENSE, and GENERAL_EVACUATION. FLOOD means `가정 침수영역에 따른 영향 시뮬레이션`, not physical flood prediction.
- Added same-origin production serving, `Dockerfile`, `/healthz`, deployment boundary docs, public license/privacy/claim audits, and final release manifest. Local production smoke observed HTTP 200 for health, root UI, readiness, and mode contract.
- Generated the official-template-based HWPX working copy and five-page review PDF. Identity, signature, consent, and certificate fields remain explicitly human-owned.
- Public deployment and GitHub push remain `FINAL_RELEASE_B` human actions because this workspace has no configured remote or authenticated hosting session. No public URL is claimed.
- Expanded the audit to cover Goal 0 through Goal 9; all locally verifiable goal flags are true, with only the three external terrain/rainfall gates remaining false.
