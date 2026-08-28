FROM node:22-alpine AS web-build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.ts tsconfig.json ./
COPY public ./public
COPY apps ./apps
COPY data/processed ./data/processed
COPY data/manifests ./data/manifests
RUN npm run build

FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY services ./services
COPY models ./models
COPY data/processed ./data/processed
COPY data/scenarios ./data/scenarios
COPY data/manifests ./data/manifests
COPY data/raw/openstreetmap ./data/raw/openstreetmap
COPY --from=web-build /app/dist ./dist
RUN test -r data/processed/anyang_facilities.json \
    && test -r data/processed/anyang_population.json \
    && test -r data/processed/anyang_local_resources.json \
    && test -r data/scenarios/goal4a/anyang-general-evacuation-competition.json \
    && test -r data/raw/openstreetmap/anyang_pedestrian_demo/overpass.json \
    && test -r data/raw/openstreetmap/anyang_pedestrian_broad/overpass.json \
    && test -r models/scenario_triage/model.joblib \
    && test -r data/manifests/data_manifest.json
EXPOSE 8080
CMD ["sh", "-c", "python -c 'from pathlib import Path; required=[\"data/processed/anyang_facilities.json\",\"data/processed/anyang_population.json\",\"data/processed/anyang_local_resources.json\",\"data/scenarios/goal4a\",\"data/raw/openstreetmap/anyang_pedestrian_demo/overpass.json\",\"data/raw/openstreetmap/anyang_pedestrian_broad/overpass.json\",\"models/scenario_triage/model.joblib\",\"data/manifests/data_manifest.json\"]; missing=[p for p in required if not Path(p).exists()]; raise SystemExit(1) if missing else None' && uvicorn services.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
