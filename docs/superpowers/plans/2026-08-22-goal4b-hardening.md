# SAFE-Twin Anyang Goal 4B Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the Goal 4A administrative 4D simulator into a deterministic, profiled, cached, provenance-safe competition demo without changing the frozen terrain or citizen-routing boundary.

**Architecture:** Keep the existing FastAPI/React simulator and add a compile layer around immutable scenario state signatures. Separate official source reconciliation from simulation demand allocation, and expose affected-demand, participation, provenance, causal A/B, and explanation data through the existing admin API. Preprocess the bounded OSM graph once, use indexed hazard candidates, compile unique states, and serve playback from an in-process/versioned cache with exact uncached-equivalence tests.

**Tech Stack:** Python 3, FastAPI, NetworkX, Shapely/STRtree if available, JSON artifacts, React/TypeScript, Playwright, Vitest, pytest.

**Spec:** `C:\Users\owner\.codex\attachments\3822e6c1-09e1-4903-8d30-6f8a99148365\pasted-text.txt`

## Global Constraints

- `FINAL_TERRAIN_CLASS = TERRAIN_C`; no terrain-derived flood depth, PhysicsNeMo, or citizen hazard routing.
- National filtered facilities must be labeled `NATIONAL_OFFICIAL_FILTERED_ANYANG`; they are not `ANYANG_LOCAL_OFFICIAL`.
- Official population totals remain 31 units and 562,143 residents as of 2026-07-31.
- Spatial allocation remains `SIMULATED_SPATIAL_ALLOCATION` unless an official polygon source is acquired; no census-grid or resident-location claims.
- `assigned + unserved = evacuation_demand`; facility load never exceeds effective capacity.
- No AI, LLM, automatic dispatch optimization, or fabricated official metrics.
- Every performance claim must come from a fresh benchmark artifact on the same bounded Goal 4A AOI.

### Task 1: Freeze and audit the current Goal 4A boundary

**Files:**
- Read: `docs/GOAL4A_DECISION.md`, `docs/FOUR_D_STATE_MODEL.md`, `docs/EVACUATION_ASSIGNMENT_MODEL.md`, `docs/ANYANG_RESOURCE_MODEL.md`, `docs/ANYANG_LOCAL_DATA_CROSSWALK.md`, `docs/ANYANG_SHELTER_CROSSWALK.md`, `docs/DATA_AND_LICENSES.md`, `docs/BLOCKED_DATA.md`, `docs/PROGRESS.md`, `data/manifests/data_manifest.json`
- Create: `artifacts/evals/data/goal4b-boundary-audit.json`
- Create: `scripts/evals/audit_goal4b_boundary.py`

- [ ] Enumerate frozen terrain/citizen-routing flags and current national/local provenance labels.
- [ ] Run the audit and assert no `WATER_DEPTH_M` or citizen route response is reachable from Goal 4A.
- [ ] Record the audit artifact before code changes.

### Task 2: Acquire and inventory current login-free official data

**Files:**
- Modify: `scripts/data/fetch_sources.py`, `scripts/data/audit_sources.py` only where existing provider patterns support the new sources.
- Create: `scripts/data/audit_goal4b_local_sources.py`
- Create: `artifacts/evals/data/goal4b-local-source-audit.json`
- Modify: `data/manifests/data_manifest.json`, `docs/BLOCKED_DATA.md`, `docs/DATA_AND_LICENSES.md`

- [ ] Search current official Anyang/data.go.kr catalog endpoints for local shelters, emergency-water, flood-response inventory, drainage pumps, public buildings, and administrative-dong polygons.
- [ ] Download every login-free source that is actually available; record provider, title, URL, timestamp, hash, rows, schema, period, license, filter logic, CRS, and status.
- [ ] Record a precise human-only blocker for each unavailable source and continue without blocking the rest.
- [ ] Ensure national filtered records use `NATIONAL_OFFICIAL_FILTERED_ANYANG` and local records use `ANYANG_LOCAL_OFFICIAL`.

### Task 3: Reconcile local/national facilities and improve population geometry

**Files:**
- Create or modify: `scripts/data/crosswalk_goal4b_facilities.py`
- Create: `artifacts/evals/data/goal4b-shelter-crosswalk.json`, `artifacts/evals/data/goal4b-water-crosswalk.json`
- Modify: `docs/ANYANG_SHELTER_CROSSWALK.md`, `docs/ANYANG_LOCAL_DATA_CROSSWALK.md`, `docs/ANYANG_RESOURCE_MODEL.md`
- Create: `docs/POPULATION_SPATIAL_ALLOCATION.md`
- Modify: `services/simulator/data.py`, `services/simulator/contracts.py`
- Test: `tests/test_goal4b_data_quality.py`

- [ ] Normalize names, road addresses, parcel addresses, and coordinates with conservative matching; preserve exact/strong/ambiguous/local-only/national-only records without silent merges.
- [ ] Use emergency-water capacity only when the source actually contains a verified capacity field; never map it to shelter capacity.
- [ ] If official dong polygons are available, validate 31/31 code reconciliation, geometry validity, CRS, and population conservation.
- [ ] Replace simulated point anchors with explicit polygon-based `SIMULATED_SPATIAL_ALLOCATION` nodes only when polygons are available; otherwise preserve the current anchor fallback and document the blocker.
- [ ] Add tests for duplicate handling, source provenance retention, crosswalk non-destructive behavior, and allocation sum conservation.

### Task 4: Add affected demand and participation assumptions

**Files:**
- Modify: `services/simulator/contracts.py`, `services/simulator/engine.py`, `services/simulator/presets.py`
- Modify: `services/api/goal4a.py`, `apps/web/src/AdminSimulator.tsx`
- Modify: `docs/EVACUATION_ASSIGNMENT_MODEL.md`, `docs/FOUR_D_STATE_MODEL.md`
- Test: `tests/test_goal4b_demand.py`, `tests/test_goal4a_assignment.py`

- [ ] Add `evacuation_fraction` with explicit default `1.0` and `ADMIN_SCENARIO_ASSUMPTION` provenance.
- [ ] Derive `affected_population` from hazard containment, explicit selected demand units, affected-dong fractions, or citywide civil-defense intent; do not evacuate all residents for local polygons.
- [ ] Compute integer `evacuation_demand` deterministically and expose total population, affected population, evacuation demand, assigned, and unserved separately.
- [ ] Add UI wording `대피 참여율 가정` and deterministic conservation/error states.

### Task 5: Profile before optimization and persist static preprocessing

**Files:**
- Create: `scripts/evals/profile_goal4b.py`
- Create: `services/simulator/preprocess.py`
- Create: `data/processed/simulator/anyang_graph_preprocess.json`
- Create: `artifacts/evals/performance/goal4b-profile-before.json`
- Create: `docs/GOAL4B_PERFORMANCE_PROFILE.md`
- Test: `tests/test_goal4b_preprocess.py`

- [ ] Measure scenario parsing, geometry, hazard-road intersection, graph mutation, snapping, shortest paths, OD generation, min-cost flow, bottleneck extraction, serialization, and API overhead separately.
- [ ] Persist a versioned preprocess artifact keyed by OSM/facility/demand hashes and AOI version.
- [ ] Precompute compact graph edges, components, bounds, snaps, eligibility, lengths, and bounded AOI membership.

### Task 6: Implement indexed state compilation and exact caches

**Files:**
- Modify: `services/simulator/engine.py`, `services/api/goal4a.py`
- Create: `services/simulator/compile.py`
- Create: `services/simulator/cache.py`
- Test: `tests/test_goal4b_cache.py`, `tests/test_goal4b_equivalence.py`

- [ ] Build deterministic road, facility, demand, and resource state signatures from actual computational state plus rule/data versions.
- [ ] Use STRtree or the maintained equivalent for bbox candidate selection and exact hazard-segment checks.
- [ ] Reject zero-capacity, unavailable, ineligible, disconnected, zero-demand OD pairs before shortest-path work.
- [ ] Compile each unique scenario state once, reuse unchanged timestamps, and expose `READY`, `CALCULATING`, `CACHED`, and `FAILED` status.
- [ ] Keep exact NetworkX min-cost flow unless the profile proves it is material; do not introduce approximation.
- [ ] Test cache invalidation for road, facility capacity, demand, and source-version changes, plus exact cached/uncached output equivalence.

### Task 7: Add affected-demand, causal A/B, and why traces to the API/UI

**Files:**
- Modify: `services/api/goal4a.py`, `apps/web/src/AdminSimulator.tsx`, `apps/web/src/styles.css`
- Test: `tests/test_goal4b_api.py`, `apps/web/src/App.test.tsx`, `tests/e2e/goal4b.spec.ts`

- [ ] Return deterministic causal state diffs for changed roads, facilities, capacities, affected population, and participation.
- [ ] Add an assignment explanation endpoint/panel based only on solver state and fixed templates.
- [ ] Add a compact data/provenance panel listing provider, date, count, role, and provenance.
- [ ] Show affected population, evacuation demand, assigned, unserved, available shelter capacity, changed roads/facilities, and computation status.

### Task 8: Demo mode and preset story hardening

**Files:**
- Modify: `apps/web/src/App.tsx`, `apps/web/src/AdminSimulator.tsx`, `services/simulator/presets.py`
- Modify: `tests/e2e/goal4b.spec.ts`
- Create: `docs/COMPETITION_DEMO_FLOW.md`

- [ ] Implement `/admin?demo=1` with a prepared scenario, Anyang extent, clean state, obvious play button, and safety labels.
- [ ] Ensure civil-defense, fire, flood exercise, and general evacuation presets have distinct deterministic causal stories; earthquake remains schema/demo only if coverage is incomplete.
- [ ] Keep normal admin functionality and remove only development-heavy controls from demo presentation mode.

### Task 9: Benchmark after and full end-to-end/visual verification

**Files:**
- Modify: `scripts/evals/benchmark_goal4a.py` or create `scripts/evals/benchmark_goal4b.py`
- Create: `artifacts/evals/performance/goal4b-runtime-before.json`, `artifacts/evals/performance/goal4b-runtime-after.json`
- Create: `artifacts/evals/ui/goal4b-visual-review.md`
- Modify: `tests/e2e/goal4b.spec.ts`

- [ ] Measure cold compile, uncached solve, cached retrieval, playback fetch, A/B compare, graph preprocessing, memory, median/P90/P95/max on the same AOI.
- [ ] Capture and inspect 390×844, 430×932, 768×1024, 1024×768, 1280×720, and 1440×900 in demo, mid-scenario, A/B, facility detail, provenance, calculating, and large-text states.
- [ ] Run desktop/mobile keyboard, reduced-motion, compile status, manual edit, participation, explanation, provenance, export, demo, and axe checks.

### Task 10: Documentation, claim audit, and final gate

**Files:**
- Create: `docs/GOAL4B_DECISION.md`
- Modify: `docs/PROGRESS.md`, `docs/GOAL4A_DECISION.md`, `docs/DATA_AND_LICENSES.md`, `docs/BLOCKED_DATA.md`, `data/manifests/data_manifest.json`
- Create: `scripts/evals/audit_goal4b_claims.py`

- [ ] Search all source/UI/docs for unsupported flood prediction, real-time population, safe-route, predicted-depth, and real-emergency claims.
- [ ] Run full Python, Vitest, build, anti-slop, secret, Playwright, axe, data-quality, equivalence, and benchmark commands.
- [ ] Report exact data, blockers, before/after profile, cache latency, equivalence, invariants, A/B numeric delta, demo status, and next AI goal without starting it.
