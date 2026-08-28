# Goal 7A — Public Core Recovery

Status: implementation and local regression complete; Render deployment verification pending.

## Root-cause record

### Citizen route

- Symptom: route UI previously failed on public; local E2E also exposed that a route arriving before MapLibre `load` could be lost because the source was created from the initial `walkingRoute` closure and the update effect had already run.
- Root cause: MapView initialization captured first-render dynamic props. The route source could remain empty when the response completed before map load.
- Why old tests missed it: the recovery test asserted a DOM test id/legend, not GeoJSON source data.
- Code changed: `MapView.tsx` now keeps current dynamic props in refs, initializes sources from those refs, fits an initial route, and exposes the map instance as `window.__SAFE_TWIN_MAP__` for E2E inspection.
- New behavioral test: `tests/e2e/public-p0.spec.ts` checks the real `walking-route` source contains a LineString with at least two coordinates.

### Citizen 4D simulation

- Symptom: timer advanced while the selected competition preset had no metric change between its first two frame times.
- Root cause: the preset is unchanged from 0 to 10 minutes for the displayed metrics; the existing engine changes later. This was a demo-preset selection problem, not fabricated data.
- Why old tests missed it: they checked visible controls/metrics but did not compare frame JSON across the first playback transition.
- Code changed: the citizen training preview selects the existing `anyang-civil-defense-outage` preset, whose 0→10 frame has a real available-shelter state change. No values are hard-coded.
- New behavioral test: public P0 test fetches both real frames, asserts server JSON differs, then waits for the changed visible value.

### Admin initialization

- Symptom: public admin previously remained in scenario-loading state despite a successful scenario-list response.
- Root cause: initialization used independent effects for list, scenario, and frame, allowing stale/overlapping asynchronous responses and leaving no bounded diagnostic state.
- Why old tests missed it: local recovery coverage did not assert request lifecycle or stale-response protection.
- Code changed: AdminSimulator now uses request generation IDs, bounded requests, explicit `LOADING_SCENARIO`/`LOADING_FRAME`/`ERROR` status text, per-endpoint status/elapsed diagnostics, and deployment identity display.
- New behavioral test: public P0 test requires admin READY, actionable playback, and changed frame metrics.

### Deployment identity and cache

- Code changed: added `GET /api/release/version`, Docker ARG/ENV propagation for commit/build identity, shared frontend build ID injection, and bumped the service-worker shell cache from v2 to v3. Existing API bypass and network-first navigation behavior remain enforced.
- The public deployment must be rechecked after push; no public result is claimed before the live version endpoint and no-mock suite pass.

## Regression evidence

- Python: `100 passed, 1 skipped, 40 warnings`.
- Vitest: `5 passed`.
- New no-mock P0 E2E against local production dist: `4 passed` after route-source assertion and real frame-difference assertion.
- Docker: unavailable in this host because Docker Desktop's Linux engine named pipe was absent; prior production-container evidence remains in `docs/PRODUCTION_RECOVERY.md`, but this Goal 7A change set still needs a fresh Docker run.
- Public Render: pending deployment of this change set.

## Release gate

Do not classify as `P0_PUBLIC_CORE_A` until the five required public workflows pass: citizen route, citizen simulation visible change, admin READY, admin playback visible change, and A/B comparison. Until then the classification remains `P0_PUBLIC_CORE_C`.
