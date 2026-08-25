# SAFE-Twin Anyang

안양시 공공데이터를 기반으로 재난 가정에 따른 도로·대피시설·수용량·인구 수요를 시간축에서 재계산하고, AI가 다수의 What-if 후보를 선별한 뒤 exact 시뮬레이터로 재검증하는 4D 행정 의사결정 지원 서비스입니다.

The release is an administrative multi-hazard What-if prototype, not a physical flood-prediction or citizen-safe-route product. See [docs/FINAL_PRODUCT_SCOPE.md](docs/FINAL_PRODUCT_SCOPE.md), [docs/FINAL_RELEASE_DECISION.md](docs/FINAL_RELEASE_DECISION.md), and [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Start locally:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_demo.ps1
powershell -ExecutionPolicy Bypass -File scripts/smoke_demo.ps1
```

Open `http://127.0.0.1:5173/admin?demo=1`. The demo requires exact verification for AI-shortlisted scenarios. It does not provide flood-depth prediction, terrain-based citizen routing, official emergency forecasting, or real-time population.
