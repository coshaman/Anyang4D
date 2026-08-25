FROM node:22-alpine AS web-build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.ts tsconfig.json ./
COPY public ./public
COPY apps ./apps
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
EXPOSE 8080
CMD ["sh", "-c", "uvicorn services.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
