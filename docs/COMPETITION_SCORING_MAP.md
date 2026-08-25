# 경쟁 심사 기준 대응 지도

| 기준 | 목표 주장 | 근거 | 그림/표 | 정량값 | 약점 | 완화 |
|---|---|---|---|---|---|---|
| 공공데이터 | 안양 자료가 계산 입력이다 | consistency, manifest, crosswalk | Fig. 6, 데이터 표 | 224/231 shelters, 46/71 water, 305 AED, 31동/562,143명 | 일부 자료는 맥락용 | 역할을 demand/capacity/network/resource로 분리 |
| AI | AI는 많은 What-if 후보를 선별한다 | reproducibility, model card | Fig. 5, AI 표 | 160 scenarios, 28 features, validation Spearman .977020, OOD .964430 | OOD와 cost-tail 약점 | DEMO_ONLY, exact top-K 필수 |
| 독창성 | 시간 변화·용량·A/B·AI/exact 결합 | exact engine, fixed A/B | Fig. 3–5 | cost +1,001,955.9m, shelters -1 | generic map/AI로 오해 가능 | workflow 중심으로 설명 |
| 완성도 | 실제 동작 가능한 심사 prototype | smoke, browser, build, tests | Fig. 1–6 | 91 Python, 5 Vitest, 18 Playwright | cold start/OSM 외부 의존 | 고정 demo, fail-safe, latency 공개 |
| 확장성 | 공식 feed와 타 지자체로 확장 가능 | roadmap, canonical state | architecture | 공식 feed·동 경계·추가 resource 계획 | 실제 운영 배포는 미완 | 단계별 검증 조건과 human action 공개 |

## 독립 심사 관점

- 공공데이터 심사자는 “안양 데이터가 실제 계산에 영향을 주는가”를 물을 가능성이 높다. 대피 수요 31개 동, 시설 용량, 최단경로와 A/B 결과로 답한다.
- AI 심사자는 “Ridge가 왜 AI인가, 틀리면 어떻게 하나”를 물을 가능성이 높다. 순위 지표·OOD·exact 검증·DEMO_ONLY 경계를 함께 제시한다.
- 공공안전 심사자는 예측·안전 보장 여부를 물을 가능성이 높다. 행정 가정 What-if와 시민 화면 분리, terrain 제외를 분명히 한다.
- 제품 심사자는 25초 대기와 운영성을 물을 가능성이 높다. 20개 동일 실행 1.78배, 100개 대표 24.889초, N=1000 미측정이라는 제한을 먼저 공개한다.

주요 감점 가능성은 실시간 hazard feed 부재, simulated population anchors, terrain flood path 제외, 100-candidate batch latency다. 이를 기능 완료처럼 포장하지 않고 검증-driven scope control과 현실적인 roadmap으로 완화한다.
