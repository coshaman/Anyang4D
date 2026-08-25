# Public deployment boundary

The production target is a single-origin FastAPI service serving the Vite `dist/` at `/` and API routes under `/api`. `Dockerfile` builds the frontend and packages the validated backend, model, processed data, scenarios, and OSM demo graph. Health is `/healthz`; product readiness is `/api/release/readiness`.

No public HTTPS endpoint is claimed until a human authenticates the hosting provider and the smoke suite records a real response. Local smoke evidence is explicitly labeled local.

Target repository: `https://github.com/coshaman/Anyang4D`, branch `main`. The repository has no configured remote in this workspace, so pushing is a human-authenticated action.
