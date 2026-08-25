# Deployment

## Single-service production runtime

The production image builds the Vite frontend and serves it from the FastAPI process. API routes remain under `/api`; the frontend uses same-origin `/api` in production and the local 8000 API during Vite development.

```powershell
docker build -t safe-twin-anyang .
docker run --rm -p 8080:8080 safe-twin-anyang
```

Open `http://127.0.0.1:8080/admin?demo=1`.

## Checks

- `GET /healthz` returns service health.
- `GET /api/release/readiness` returns the validated release core.
- `GET /api/foundation` confirms official-data mode.
- `GET /api/admin/goal4a/scenarios` confirms the demo scenario store.
- `POST /api/admin/goal5a/screen` followed by exact verification confirms the AI workflow.

No secret is required for the default demo. The public image excludes raw NGII terrain, private team files, official forms, local caches, and restricted provider files. The bounded OSM snapshot is retained with ODbL attribution.
