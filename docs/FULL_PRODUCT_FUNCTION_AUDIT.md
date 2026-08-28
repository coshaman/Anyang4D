# SAFE-Twin Anyang Full Product Functional Audit

Audit date: 2026-08-29. Target: `https://anyang4d.onrender.com`. Scope was audit-only; no production behavior, tests, or acceptance criteria were changed.

## Executive result

| Area | Total | Public Functional | Broken | Missing | Partial / unverified | Intentionally Disabled |
|---|---:|---:|---:|---:|---:|---:|
| All listed features | 179 | 60 | 27 | 0 | 92 | 0 |

“Partial / unverified” includes `CODE_ONLY`, `LOCAL_FUNCTIONAL` without public proof, `VISUALLY_INEFFECTIVE`, and `PERSISTENCE_LIMITED`. This is deliberately conservative: a green API or a visible button is not a functional pass.

## Direct answers

1. Basic walking route truly draws: **local yes; public no**. Public UI ended in the route-load failure message. The local route displayed geometry and distance/time; the public result did not.
2. Citizen simulation visibly changes over time: **no on public**. The timer moved from 0 to 10 minutes, but metrics and dynamic map results did not appear.
3. Admin playback visibly changes over time: **local yes; public unavailable**. Local frame 0/10 produced different computed metrics; public admin remained in scenario-loading state.
4. Training route genuinely usable: **not complete**. Backend source returns geometry, but frontend only writes status text and does not pass a training geometry layer to `MapView`.
5. New scenario save genuinely works: **implemented and locally writable by source/API path, not publicly proven**. No public write was issued to avoid mutating the live service.
6. Persistence: **instance-lifetime / persistence-limited**, using `data/scenarios/goal4a` JSON in the running filesystem; no durable Render volume was evidenced.
7. Hazard drawing: **code-only/unverified end-to-end**; no automated behavioral test or current successful authoring capture.
8. Road closure authoring: **implemented but practically weak**; it requires an opaque manually entered edge ID and was not reachable in the public loading state.
9. Facility close/capacity: **local source/API path present, public unverified**; no end-to-end behavioral test proves binding assignment changes through UI.
10. Resource editing: **selector/labels public functional; mutation/effect unverified**.
11. A/B: **local functional smoke result; public blocked by admin load**. Current local result showed deltas and causal explanation.
12. AI without mocks: **not functional on public**; the real 100-candidate POST timed out at 60 seconds. Existing E2E coverage is mocked.
13. Major public browser/network errors: no console errors were observed, but route UI failed, simulation was visually ineffective, admin stayed loading, and AI POST timed out. See `artifacts/evals/functional-audit/public-console.log` and `public-network.json`.

## Feature checklist

Each ID is listed once; details for every FAIL/PARTIAL group are below and the complete evidence columns are in `docs/FULL_PRODUCT_FUNCTION_MATRIX.md`.

### PASS — public functional (60)

`C01 C02 C03 C04 C05 C06 C07 C10 C11 C12 R01 R02 S01 S02 S04 A01 A06 RR01 RR02 PD01 PD03 PD05 PD06 PD07 PD08 PD10`

### FAIL — public broken (27)

`R03 R06 R07 R08 R09 R10 R11 R12 R15 A02 A03 A04 A05 A07 A10 A11 A12 A13 A14 A15 A16 A17 A19 T01 N01 N06 D01 H01 RC01 F01 AB01 AB02 E01 AI01 AI02 AI05 AI07 AI08 AI09 AI10 AI11 AI12 M03 M04`

### PARTIAL / locally proven only / visually ineffective (92)

`C08 C09 R04 R05 R13 R14 S07 A08 A18 T02 T03 T04 T05 T06 T08 T10 T11 T12 N02 N03 N04 N05 N07 N08 N09 N10 N11 N12 D02 D03 D04 D05 H02 H03 H04 H05 H06 H07 H08 H09 H10 H11 H12 RC03 RC04 RC05 RC06 RC07 RC08 F02 F03 F04 F05 F06 F07 F08 F09 F10 F11 RR03 RR04 RR05 RR06 AB03 AB04 AB05 AB06 AB07 AB08 AB09 AB10 AB11 E02 E03 E04 E05 E06 E07 AI03 AI04 AI06 PD02 PD04 PD09 M01 M02 M08 S03 S05 S06 S08 S09 S10 S11 S12 S13 S14 S15 S16 S17 T09 RC02 M05 M06 M07 T07 N13 N14 D06`

The count includes every matrix row; IDs with a public failure plus an unverified sub-behavior are retained as separate rows rather than being hidden by the parent failure.

## FAIL/PARTIAL findings and repair scope

### Public route and map (R03–R15, M03–M04)

- Observed: selecting a coordinate-bearing shelter and clicking `기본 도보 경로 보기` produced `도보 경로를 불러오지 못했습니다...`; no public line, endpoints, distance/time, or fit result appeared.
- Expected: POST `/api/routes` returns nonempty geometry and the frontend stores it in a `walking-route` GeoJSON source with rendered line and endpoint markers.
- Frontend/backend: `apps/web/src/App.tsx`, `apps/web/src/MapView.tsx`; `services/api/main.py:routes`, `services/api/routing.py:build_route`.
- Hypothesis/confidence: public deployed bundle/API consumer parity or runtime route failure; **medium**, because public browser showed the failure but console contained no exception. Local route worked.
- Severity: P0 for R03–R08/M03; P1 for markers/fit/text. Evidence: `screenshots/public-route-after.png` if present, public console/network logs, local route screenshot, API matrix.
- Repair scope: trace public request/response and deployed asset version, then restore route state-to-MapLibre source wiring; add source/rendered-feature assertions. **Large**.

### Citizen simulation (S03–S17, M05–M07)

- Observed: scenario list and timeline loaded; play changed 0 to 10 minutes, but no computed metric block or meaningful dynamic map state appeared.
- Expected: frame JSON at 0/10/20/30 and visible hazard, closed-road, facility-load, demand, assigned, unserved, available-shelter, and changed-road changes.
- Frontend/backend: `CitizenSimulationPreview.tsx`, `MapView.tsx`; Goal 4A scenario/frame endpoints.
- Hypothesis/confidence: public frontend is stale or frame-consumer transition is failing despite healthy GET APIs; **medium**.
- Severity: P0. Evidence: current public simulation t0/t10 screenshots and `public-api-matrix.json`; local admin frame metrics prove the engine can change state.
- Repair scope: align public build with current source, capture frame responses in browser, bind all frame fields to visible metrics/layers, and add 0/10/20/30 rendered-state tests. **Large**.

### Admin loading/playback (A02–A19, AB01–AB02, E01, N01/N06, D01, H01, RC01, F01, AI01)

- Observed: public admin page loaded and resource list appeared, but scenario detail remained `시나리오를 불러오는 중입니다.` and readiness remained `확인 중`; dependent controls were unavailable. Responsive capture showed the sidebar is very long and key controls are below fold; buttons measured about 42px high.
- Expected: persisted preset selected, frame 0/metrics/readiness loaded, then playback, compare, export, authoring, and AI controls become actionable.
- Frontend/backend: `AdminSimulator.tsx`; `/api/admin/goal4a/scenarios`, scenario detail/frame/resources, `/api/release/readiness`, compare/export/authoring endpoints.
- Hypothesis/confidence: public consumer does not complete scenario-detail/frame state transition or is serving an incompatible/stale asset; **medium**. GET scenario list was 200, so list availability alone is insufficient.
- Severity: P0 for playback/A-B; P1 for authoring/export/AI reachability. Evidence: `screenshots/public-admin-*.png`, `public-console.log`, API matrix.
- Repair scope: instrument detail/frame request lifecycle and deployment asset identity, fix loading/error state, then test all dependent controls at five viewports. **Large**.

### Training route (T01–T12)

- Observed: local backend path can return route geometry and local UI displays a text result, but `AdminSimulator.tsx` only sets `routeStatus`; no training geometry is passed to `MapView`. Public control was unreachable.
- Expected: request payload includes scenario/time/origin/destination, response contains geometry, and a clearly distinguished training route is drawn and changes with closures.
- Hypothesis/confidence: confirmed frontend integration gap; **high** from source inspection. Severity P1.
- Evidence: `services/api/goal4a.py:training_route`, `services/simulator/engine.py:build_training_route`, local training screenshot, coverage audit.
- Repair scope: add dedicated route state/source/layer and behavioral closure-sensitive tests. **Medium**.

### Authoring, persistence, and edits (N/D/H/RC/F/RR)

- Observed: source exposes controls and ScenarioStore writes JSON under `data/scenarios/goal4a`; public authoring could not be reached without mutating the live deployment, and no existing tests exercise the full UI flows. Road editor accepts an opaque ID such as `123-456`.
- Expected: create/duplicate/draw/edit/save effects appear immediately, survive refresh, and persistence durability is accurately communicated.
- Hypothesis/confidence: local instance-lifetime behavior is **high confidence** from `services/simulator/storage.py`; Render redeploy durability is **unknown**, therefore classified persistence-limited, not durable.
- Severity: P1 for authoring/effects, P2 for edge discoverability. Evidence: source, test gap audit, public admin screenshots.
- Repair scope: add isolated behavioral fixtures for each mutation, expose map-selectable validated road IDs, and make storage durability explicit. **Medium–large**.

### AI (AI02, AI05–AI12)

- Observed: direct public POST `/api/admin/goal5a/screen` timed out after 60 seconds. Existing Playwright AI test uses a fulfilled mock response.
- Expected: real model load, estimate, support, exact top-K verification, visually distinct estimate/exact result, authoritative exact output, and elapsed time.
- Frontend/backend: `AdminSimulator.tsx`; Goal 5A screen endpoint/model.
- Hypothesis/confidence: public runtime capacity or request execution issue; **medium**. Severity P1.
- Repair scope: bounded async job/timeout UX and real end-to-end performance/error instrumentation; then remove mock-only release confidence. **Large**.

## Local / Docker / public parity for P0/P1

| Feature | Local | Real Docker | Public Render |
|---|---|---|---|
| Health/readiness | PASS | PASS | PASS |
| Citizen route | PASS | PASS | FAIL |
| Simulation frames/metrics | PASS in current source/admin evidence | PASS in production-container evidence | VISUALLY INEFFECTIVE |
| Admin scenario/frame load | PASS | PASS | FAIL/loading |
| A/B comparison | PASS smoke | PASS API evidence | BLOCKED by admin load |
| Training route | backend PASS, map partial | backend PASS | UNVERIFIED/BLOCKED |
| AI screen | local code path | readiness PASS | TIMEOUT |
| Persistence | filesystem instance | container filesystem | durability unknown; limited |

## Top five P0/P1 issues and repair order

1. Public route-to-map rendering — P0 — restore request/state/source parity.
2. Public citizen simulation visible frame output — P0 — restore frame consumer and dynamic layers.
3. Public admin scenario/frame loading — P0 — unblock playback, A/B, export, and authoring.
4. Training-route geometry integration — P1 — render backend geometry, not text only.
5. Real AI screen timeout/model execution — P1 — bounded runtime and exact-verification evidence.

Recommended order: deployment parity and route tracing → simulation/admin loading → visible training route → real AI → authoring/persistence tests → responsive/polish.

## Release verdict

**FUNCTIONAL_RELEASE_C** — core advertised public route, 4D simulation, admin playback, and real AI screening are broken or incomplete. Docker/test success and a green Render service response do not change this public functional verdict.
