# Goal 7A-R runtime recovery result

Date: 2026-08-29 (KST)

## Classification

`B_PUBLIC_STABLE_OLD_DEPLOYMENT_PENDING`

The pre-fix public runtime probe was `INTERMITTENT_502_OR_UNAVAILABLE`: 30 requests across six iterations, 8 successful responses and 22 failures/unavailable responses, including 502 and 503 responses from `/healthz`, `/readyz`, release endpoints, and the Goal 4A scenario list.

After the probe window, the existing public deployment became stable enough for a fresh no-mock browser run: route rendering, citizen simulation frame change, admin READY/playback, and exact A/B comparison all passed (4/4). Its reported deployment identity remained `20b210e473d6f0ff8ff90c7ca02a72fdc5ba24b1`.

The runtime-hardening fix was committed and pushed to `main` as `92eafb5`, but the public service continued reporting the older identity throughout the post-push observation window. Therefore this is not classified as `RENDER_RUNTIME_A`: the same-latest-deployment condition is not proven.

## Implemented fix

- Cached the mandatory readiness payload so repeated `/readyz` and `/api/release/readiness` requests do not reconstruct the data/graph pipeline.
- Kept `/healthz` independent of optional release fingerprint metadata.
- Added safe JSON response parsing so HTML/empty 502 responses become visible endpoint-specific errors instead of JSON parse exceptions.
- Documented `/healthz` as the cheap Render/container health-check path.

## Local evidence

- Vitest: 7 passed.
- Vite production build: passed.
- Python targeted release/API tests: 8 passed.
- Full Python suite: 99 passed, 2 skipped, 4 failures caused by absent historical/raw artifacts or a pre-existing frozen-plan/audit mismatch in this clean clone.
- Fresh-process memory observation showed no growth after the one-time readiness/frame load; RSS remained about 238 MB across healthz, readyz, readiness, and frame phases.

## Required human action

In the Render Dashboard, manually deploy the `main` branch (or re-enable/trigger automatic deploy) and set the service health-check path to `/healthz`. Then rerun the Goal 7A-R probe and fresh P0 suite against the deployment reporting `92eafb5`.
