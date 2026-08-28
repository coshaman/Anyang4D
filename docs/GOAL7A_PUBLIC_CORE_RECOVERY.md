# Goal 7A — Public Core Recovery

Status: public P0 workflows recovered; release fingerprint injection remains a hosting-configuration follow-up.

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
- Public `/api/release/version` is live after the push, but Render reports `unknown` for both API commit and frontend build ID because the service does not inject the Docker build ARG. The unsafe alternative of sending `.git` history in the build context was rejected.

## Regression evidence

- Python: `100 passed, 1 skipped, 40 warnings`.
- Vitest: `5 passed`.
- New no-mock P0 E2E against local production dist: `4 passed` after route-source assertion and real frame-difference assertion.
- Public Render no-mock E2E: `3 passed` in the first four-test run; the remaining A/B test passed on isolated retry after a transient Render 502 during cold-start. Direct readiness, scenario, and frame checks subsequently returned 200/READY.
- Public evidence: `artifacts/evals/goal7a/public-route-base.png`, `public-route-result.png`, `public-citizen-simulation.png`, `public-admin-ready.png`, `public-ab-result.png`, and `public-citizen-frames.json`.
- Docker: unavailable in this host because Docker Desktop's Linux engine named pipe was absent; prior production-container evidence remains in `docs/PRODUCTION_RECOVERY.md`, but this Goal 7A change set still needs a fresh Docker run.
- Public Render: deployed from commit `732db92c07ae1ff1b76c466794519a5b9f94e548`; `/healthz` and `/readyz` are healthy and the live release endpoint is present. Fingerprint SHA equality is not proven because Render returns `unknown`.

## Release gate

The five required public workflows pass: citizen route, citizen simulation visible change, admin READY, admin playback visible change, and A/B comparison. Functional classification is `P0_PUBLIC_CORE_A`; deployment identity remains an explicit hosting gate until Render supplies the pushed SHA.
