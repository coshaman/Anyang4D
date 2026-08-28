# Production recovery evidence

## Root cause

The deployed shell was not a valid production-parity test target. The FastAPI image served `/` but did not serve the SPA shell for direct `/simulate` and `/admin` paths, so browser flows could not enter the product. The Dockerfile also contained a redundant mistyped facility COPY line. The frontend had a same-origin API base, but its route result was only text: no route geometry was passed to MapLibre. AED records were filtered out of the nearby textual list when coordinates were null. A final runtime log audit also found MapLibre's default worker URL pointed at an unhashed, nonexistent asset; the worker is now imported through Vite and configured explicitly.

## Recovery boundary

- `/healthz` remains liveness only.
- `/readyz` executes facility, population, demo OSM, broad OSM, scenario store, exact engine, and AI-model checks; it returns 503 with concise check details when mandatory state is unavailable.
- `/admin`, `/simulate`, and `/about-data` now receive the SPA shell in the FastAPI production runtime.
- Route geometry is rendered as the `walking-route` MapLibre line with origin/destination points and fit-to-bounds. It is basic walking-network routing, not disaster-safe routing.
- AED remains unpinned because the source has no coordinates, but its searchable address list, 119-first action, provenance, and `원문 좌표 없음` label remain visible.
- Service-worker cache is versioned to v2, API requests bypass it, navigation is network-first with shell fallback, and obsolete SAFE-Twin caches are removed on activation.
- MapLibre's worker is emitted as a hashed production asset and registered explicitly, avoiding the prior `/assets/maplibre-gl-worker.mjs` 404.

## Verified local production artifact

`tests/e2e/production-recovery.spec.ts` ran against the FastAPI-served built `dist` at `http://127.0.0.1:8092` with no mocked Goal4/Goal5 APIs: 2 passed. HTTP parity checks passed for `/healthz`, `/readyz`, readiness, scenarios, resources, AED (305 records), and POST route (nonempty geometry). The Vite build emitted `dist/assets/maplibre-gl-worker-*.mjs`.

The Docker image was then built successfully and the real container passed the HTTP production-parity test and both no-mock Playwright production tests. The first container attempt exposed a startup assertion bug (`TypeError: exceptions must derive from BaseException`); the assertion now exits only when artifacts are missing. Real public HTTPS smoke remains unrun because no Render URL or hosting authentication is available. No public URL is claimed.
