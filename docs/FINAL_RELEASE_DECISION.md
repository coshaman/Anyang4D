# Final release decision

## Classification

`FINAL_RELEASE_B`

The product is technically release-ready on the validated Goal 4B/5A/6A/6B core. FINAL_RELEASE_B reflects remaining human-only actions: GitHub/hosting authorization if a public account is used, participant identity fields, handwritten signatures, and enrollment certificates. The missing high-resolution DEM is not a release blocker and is permanently closed.

Production recovery is locally verified in `artifacts/evals/release/production-recovery.json`. `PUBLIC_READYZ_PASS=false` remains honest until a real public HTTPS deployment is authenticated and tested; this document must not be read as public deployment proof.

## Release gate

- Same-origin production artifact: `Dockerfile` serves Vite `dist` and FastAPI on one port.
- Health endpoint: `/healthz`.
- Readiness endpoint: `/api/release/readiness`.
- Main demo: `/admin?demo=1`.
- Exact solver remains authoritative; AI shortlist values are not authoritative.
- Raw NGII DXF/DEM and private team information are excluded from public deployment.
- OSM attribution and public-data provenance remain required.

## Product one-liner

안양시 공공데이터를 기반으로 재난 가정에 따른 도로·대피시설·수용량·인구 수요를 시간축에서 재계산하고, AI가 다수의 What-if 후보를 선별한 뒤 exact 시뮬레이터로 재검증하는 4D 행정 의사결정 지원 서비스
