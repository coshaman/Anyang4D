# Production recovery evidence

## Root cause

The deployed shell was not a valid production-parity test target. The FastAPI image served `/` but did not serve the SPA shell for direct `/simulate` and `/admin` paths, so browser flows could not enter the product. The Dockerfile also contained a redundant mistyped facility COPY line. The frontend had a same-origin API base, but its route result was only text: no route geometry was passed to MapLibre. AED records were filtered out of the nearby textual list when coordinates were null.

## Recovery boundary

- `/healthz` remains liveness only.
- `/readyz` executes facility, population, demo OSM, broad OSM, scenario store, exact engine, and AI-model checks; it returns 503 with concise check details when mandatory state is unavailable.
- `/admin`, `/simulate`, and `/about-data` now receive the SPA shell in the FastAPI production runtime.
- Route geometry is rendered as the `walking-route` MapLibre line with origin/destination points and fit-to-bounds. It is basic walking-network routing, not disaster-safe routing.
- AED remains unpinned because the source has no coordinates, but its searchable address list, 119-first action, provenance, and `원문 좌표 없음` label remain visible.
- Service-worker cache is versioned to v2, API requests bypass it, navigation is network-first with shell fallback, and obsolete SAFE-Twin caches are removed on activation.

## Verified local production artifact

`tests/e2e/production-recovery.spec.ts` ran against the FastAPI-served built `dist` at `http://127.0.0.1:8091` with no mocked Goal4/Goal5 APIs: 2 passed. HTTP parity checks passed for `/healthz`, `/readyz`, readiness, scenarios, resources, AED (305 records), and POST route (nonempty geometry).

The Docker daemon was unavailable on this host (`dockerDesktopLinuxEngine` pipe not found), so a Docker image build and real public HTTPS smoke were not possible here. No public URL is claimed until a human starts/authenticates Docker/hosting and runs the same gate.
