# SAFE-Twin Goal 3B Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a license-safe, provenance-gated SAFE-Twin flood engine that can run a deterministic Level-A scenario baseline now, accept real Anyang terrain/rainfall later, and expose benchmark/synthetic 4D playback without entering public routing.

**Architecture:** A pure Python engine owns `FloodScenarioInput`, `FloodScenarioOutput`, maturity gates, and a deterministic terrain/rainfall baseline. Frame storage uses compact NumPy `.npz` files plus JSON metadata so the current environment needs no new geospatial binary dependency; the contract retains CRS, transform, bounding box, resolution, and provenance for future raster upgrades. FastAPI exposes only an internal simulation-lab namespace, while the existing citizen route API remains unchanged. PhysicsNeMo is optional and isolated behind a synthetic/benchmark provenance boundary.

**Tech Stack:** Python 3.12, NumPy, FastAPI/Pydantic, pytest, TypeScript/React/Vite, Vitest, Playwright; optional PhysicsNeMo/PyTorch in a separate environment.

**Spec:** `/goal Execute SAFE-Twin Anyang Goal 3B as an autonomous overnight engineering/research goal` and `docs/GOAL3A_DECISION.md`.

## Global Constraints

- Level A means relative scenario hazard only; no Anyang water-depth claim.
- Level B requires Anyang flood observations/labels; Level C requires drainage topology and calibration observations.
- `WATER_DEPTH_M` is rejected unless the Level-C gate passes.
- Synthetic and benchmark data remain visibly labelled and cannot affect citizen routing.
- Do not vendor LarNO source or make it a runtime dependency.
- Do not destabilize the existing `.venv`; optional ML work uses a separate environment.
- Every frame records provenance, fidelity, scenario, backend, assumptions, CRS, transform, resolution, and time.

---

### Task 1: Hardware and environment evidence

**Files:**
- Create: `scripts/evals/goal3b_hardware.py`
- Test: `tests/test_goal3b_hardware.py`
- Generate: `artifacts/evals/ml/goal3b-hardware.json`

- [ ] Write a test asserting the report has OS, Python, CPU, RAM, disk, WSL, Docker, GPU, CUDA, and project-venv fields.
- [ ] Run the focused test and observe the missing module failure.
- [ ] Implement a read-only local audit using `platform`, `shutil`, `subprocess` with timeouts, and PowerShell-compatible fallbacks; never mutate `.venv`.
- [ ] Run it and record the actual environment.

### Task 2: Flood contract and fidelity gate

**Files:**
- Create: `services/flood/__init__.py`, `services/flood/contracts.py`, `services/flood/gates.py`
- Test: `tests/test_goal3b_contracts.py`

- [ ] Write failing tests for scenario input validation, output metadata, provenance, Level-A output, and rejection of Anyang depth output below Level C.
- [ ] Implement Pydantic models and `validate_output_claim(output_kind, fidelity_level, provenance)`.
- [ ] Ensure benchmark/synthetic output can exist only as internal-lab data and cannot be declared `ANYANG_OFFICIAL`.

### Task 3: Deterministic Level-A baseline

**Files:**
- Create: `services/flood/baseline.py`
- Create: `scripts/evals/goal3b_synthetic_case.py`
- Test: `tests/test_goal3b_baseline.py`

- [ ] Write failing synthetic-fixture tests for lower terrain receiving higher hazard, monotonic rainfall accumulation, nodata preservation, alignment, and metadata preservation.
- [ ] Implement finite-difference local relief, slope, simple downslope accumulation, rainfall accumulation/recession, and normalized `RELATIVE_HAZARD`/`FLOOD_CLASS` fields. Keep assumptions explicit and do not model sewer/drainage.
- [ ] Add a reproducible synthetic case and JSON summary with seed, hashes, metrics, and provenance `SYNTHETIC`.

### Task 4: 4D frame storage and internal API

**Files:**
- Create: `services/flood/storage.py`, `services/api/simulation.py`
- Modify: `services/api/main.py`
- Test: `tests/test_goal3b_storage.py`, `tests/test_goal3b_api.py`

- [ ] Write failing tests for scenario creation, time listing, frame retrieval, legend metadata, provenance warning, and missing-frame errors.
- [ ] Implement JSON metadata plus compressed NumPy frame storage under `artifacts/evals/ml/goal3b/frames/`; use atomic writes and path validation.
- [ ] Add `/api/internal/simulations/{scenario_id}`, `/times`, and `/frames/{timestamp}` endpoints. Do not alter `/api/routes` behavior.

### Task 5: Demo AOI and terrain fallback audit

**Files:**
- Create: `scripts/data/select_demo_aoi.py`
- Create: `artifacts/evals/data/demo-aoi.geojson`
- Create: `docs/DEMO_AOI.md`, `docs/NGII_DEM_DOWNLOAD_REQUEST.md`, `docs/TERRAIN_FALLBACK_AUDIT.md`
- Test: `tests/test_goal3b_aoi.py`

- [ ] Write a failing test for valid GeoJSON, bounded AOI, exact sheet list, and no duplicate sheet IDs.
- [ ] Score OSM waterways/network density, facility proximity/count, compactness, and 1 m metadata coverage without calling it hydrological risk.
- [ ] Select one compact AOI, intersect it with NGII metadata tile extents, and generate the minimum sheet request with CRS/datum/year/format and target directory.
- [ ] Audit public fallback candidates; reject coarse terrain for street-level use and label any plumbing-only use `AUXILIARY`/`BENCHMARK`.

### Task 6: Synthetic/benchmark model pipeline

**Files:**
- Create: `services/flood/pipeline.py`, `scripts/evals/goal3b_pipeline.py`
- Create: `docs/model_cards/safetwin-flood.md`, `docs/FLOOD_ENGINE_ARCHITECTURE.md`, `docs/FLOOD_ENGINE_EVALUATION.md`
- Test: `tests/test_goal3b_pipeline.py`

- [ ] Write failing tests for baseline-vs-persistence evaluation schema, split/provenance separation, metrics, and absence of Anyang claims.
- [ ] Implement a small time-varying synthetic sequence pipeline using the SAFE-Twin baseline and a persistence comparator. Keep UKEA download optional and do not use LarNO code.
- [ ] Probe PhysicsNeMo in an isolated environment if available; otherwise record exact environment/resource blockers and retain the deterministic pipeline.
- [ ] Save config, seed, metrics, latency, model size, and checkpoints/evidence under `artifacts/evals/ml/goal3b/`.

### Task 7: Internal simulation lab

**Files:**
- Modify: `apps/web/src/App.tsx`, `apps/web/src/styles.css`
- Test: `apps/web/src/App.test.tsx`, `tests/e2e/goal2.spec.ts`

- [ ] Write failing UI tests for internal simulation navigation, visible `합성 테스트 시나리오`/`벤치마크 검증 화면`, play/pause, scrubber, current time, and fidelity warning.
- [ ] Implement a technical lab view that fetches internal scenario metadata/frames or uses a clearly labelled local fixture when API is unavailable.
- [ ] Keep citizen pages and route actions free of simulation hazard state.

### Task 8: Documentation, safety, and final verification

**Files:**
- Create: `docs/GOAL3B_DECISION.md`
- Modify: `docs/BLOCKED_DATA.md`, `docs/DATA_AND_LICENSES.md` if present, `THIRD_PARTY_NOTICES.md`, `docs/PROGRESS.md`

- [ ] Record hardware, environment, exact model status, AOI, sheets, maturity, human blockers, Goal 4 authorization, and next goal.
- [ ] Run Python tests, frontend tests, production build, anti-slop, secrets, and affected Playwright tests.
- [ ] Verify no benchmark/synthetic output is reachable from citizen routing and no real Anyang claim is emitted without a Level-A gate.
