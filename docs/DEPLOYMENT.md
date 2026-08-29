# Deployment

## Single-service production runtime

The production image builds the Vite frontend and serves it from the FastAPI process. API routes remain under `/api`; the frontend uses same-origin `/api` in production and the local 8000 API during Vite development.

```powershell
docker build -t safe-twin-anyang .
docker run --rm -p 8080:8080 safe-twin-anyang
```

Open `http://127.0.0.1:8080/admin?demo=1`.

The production server explicitly serves the SPA shell for `/admin`, `/simulate`, and `/about-data`; this is covered by the production browser gate.

## Checks

- `GET /healthz` is the cheap liveness endpoint and should be configured as the Render/container health-check path; it does not load data or rebuild graphs.
- `GET /readyz` returns cached mandatory artifact/data/engine readiness and returns 503 when the app cannot execute scenarios. Its first request may perform the one-time readiness computation.
- `GET /api/release/readiness` returns the same validated release core from the cached readiness result.
- `GET /api/foundation` confirms official-data mode.
- `GET /api/admin/goal4a/scenarios` confirms the demo scenario store.
- `POST /api/admin/goal5a/screen` followed by exact verification confirms the AI workflow.
- `tests/e2e/production-recovery.spec.ts` is the no-mock production-parity browser gate; run it with `playwright.production.config.ts` against the built FastAPI-served artifact.

No secret is required for the default demo. The public image excludes raw NGII terrain, private team files, official forms, local caches, and restricted provider files. The bounded OSM snapshot is retained with ODbL attribution.
