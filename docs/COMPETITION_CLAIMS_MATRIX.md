# SAFE-Twin Anyang competition claims matrix

This is the single source of truth for competition-facing wording. Quantities below are measured from the release artifacts, not inferred from screenshots.

| Claim | Allowed wording | Forbidden wording | Evidence / provenance | Quantitative evidence | Product surface |
|---|---|---|---|---|---|
| Real Anyang public data | `안양시 실제 공공데이터를 활용합니다` | “모든 데이터가 실시간이다” | `artifacts/evals/release/data-consistency.json`; official shelter/water/AED/population files | 231 national shelters, 71 national water, 305 AED; 31 dongs / 562,143 people | Citizen banner, provenance page |
| Time-changing administrative state | `시간에 따라 도로·시설·수요 상태가 실제 계산상 변합니다` | “실제 재난이 시간에 따라 발생한다” | Goal 4B exact frame API, scenario provenance `ADMIN_SCENARIO` | Frame and A/B outputs are exact deterministic calculations | Admin timeline |
| Capacity-aware evacuation assignment | `대피시설 수용량을 고려한 exact 배정` | “실제 대피 가능성을 보장한다” | Goal 4B NetworkX min-cost flow and frame assignment | Facility availability/capacity are explicit state inputs | Admin metrics |
| AI screening | `AI가 우선 검토할 시나리오를 빠르게 선별합니다` | “AI 재난 예측”, “AI가 피해를 예측한다” | `artifacts/evals/ai/goal5a/evaluation.json`, `goal6a-ai-scale.json` | 160 scenarios, 28 features; validation Spearman 0.977020 | Admin demo only |
| Exact verification | `선택된 시나리오는 exact simulator로 재검증합니다` | “AI-verified safety” | Goal5A API response and real HTTP smoke | top-K exact calls are mandatory; smoke returned `exact_verified=true` | Admin AI panel |
| Ranking metric | `AI ranking validation Spearman = 0.977020 (measured)` | “AI accuracy 97.7%” | Evaluation artifact, grouped validation split | OOD Spearman 0.964430; Recall@20 0.85 | Technical evidence |
| Speed claim | `20개 후보에서 AI 선별 + 상위 5개 exact 재검증은 전체 exact 계산보다 1.78배 빨랐습니다` | “실시간”, “1000개 exact보다 1.78배” | Same-run scale benchmark | exact-all 32,167.964 ms vs hybrid 18,033.545 ms | Technical evidence / judge talk |
| Official population | `공식 인구 31개 동 / 562,143명` | “실시간 인구”, “실제 시민 위치” | 2026-07-31 Anyang workbook and processed population | 31 units, total 562,143; spatial anchors are simulated | Admin source panel |
| Local and national shelters | `224개 지역 대피시설 맥락 / 231개 국가 필터링 대피시설` | “224+231개가 하나의 운영 목록” | Processed crosswalk and consistency artifact | local 224; national filtered 231; kept separate | Provenance page / technical evidence |
| Local emergency water | `46개 안양시 비상급수시설 맥락` | “46개 대피 수용시설” | `anyang_local_resources.json` | 46 records; resource capacity role only | Admin source panel |
| Response inventory | `33개 수방자재 기록` | “33개가 실시간 재고” | processed local resource artifact | 33 records; dispatch optimization unauthorized | Technical evidence |

| Flood What-if boundary | `가정 침수영역에 따른 영향 시뮬레이션` | “침수 예측”, “예측 침수심”, “지형 기반 시민 안전경로” | `docs/HIGH_RES_DEM_FINAL_DECISION.md`, `ADMIN_SCENARIO` frame contract | Administrative hazard polygon only; no physical flood model | Admin What-if |

Forbidden across all surfaces: AI disaster prediction, flood prediction, predicted flood depth, safe route, real-time population, actual citizen locations, official emergency forecast, and AI-verified safety. High-resolution DEM acquisition is a closed research branch and not a release dependency. The fixed product boundary remains `TERRAIN_C`, `TERRAIN_DEPENDENCY_FOR_RELEASE=false`, street-level flood terrain path `DROP`, citizen hazard routing from terrain `DROP`, `AI_SURROGATE_B`, and `ADMIN_AI_SCENARIO_SCREENING=DEMO_ONLY`.
