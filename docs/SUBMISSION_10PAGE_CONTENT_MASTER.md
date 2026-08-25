# SAFE-Twin Anyang 제출용 10페이지 콘텐츠 마스터

> 편집 원칙: 아래 10개 페이지 블록은 공식 양식에 옮겨 넣을 수 있는 심사 본문이다. 제품 상태는 `COMPETITION_RELEASE_B`, AI는 `AI_SURROGATE_B`/관리자 데모 전용이며, 수치는 `artifacts/evals/submission/evidence-consistency.json`과 기존 release artifact를 권위 근거로 한다.

## 1쪽 | 서비스 개요와 문제

### 한 문장

SAFE-Twin Anyang은 안양시 공공데이터를 바탕으로 재난 가정에 따른 도로·대피시설·수용량·인구 수요의 변화를 시간축에서 계산하고, AI가 다수의 What-if 후보를 선별한 뒤 exact 시뮬레이터로 재검증하는 4D 행정 의사결정 지원 서비스다.

재난 대응 담당자는 “이 도로가 통제되면?”, “이 대피시설을 사용할 수 없으면?”, “영향 영역이 바뀌면 대피 수요가 어디로 이동하는가?”를 반복해서 검토한다. 단순 알림이나 시설 검색만으로는 이 변화의 연쇄효과를 비교하기 어렵다. SAFE-Twin은 가정 시나리오를 입력하고, 같은 인구 수요를 어떤 시설에 얼마만큼 배정할 수 있는지 계산 결과로 보여준다.

## 2쪽 | 사용자와 차별점

시민 화면은 공공시설 정보, AED 119 우선 안내, 기본 지도·보행 네트워크 확인과 교육용 미리보기에 집중한다. 관리자 화면은 시나리오 작성, 시간축 재생, 도로·시설 상태 변화, 용량 제약 대피 배정, A/B 비교, AI 후보 선별, exact 검증, provenance와 export를 제공한다.

기존 시민 안전 서비스의 알림·정보 전달·시설 조회와 경쟁하기보다, SAFE-Twin은 행정자가 여러 가정의 결과를 비교하는 기능에 초점을 둔다. 시민 화면에는 행정 가정 hazard, AI 선별 결과, 지형 기반 침수 출력이 연결되지 않는다.

## 3쪽 | 안양 공공데이터 활용

안양 데이터는 장식용 지도 레이어가 아니라 계산 입력이다.

| 데이터 | 제공기관 | 기준일/수집일 | 건수 | 서비스 활용 | 공식/가정 |
|---|---|---:|---:|---|---|
| 안양시 민방위 대피시설 | 안양시 | 현재 목록 / 2026-08-22 수집 | 224 | 지역 시설 맥락·crosswalk | 공식 |
| 전국 민방위 대피시설(안양 필터) | 행정안전부·LocalData | 2026-08-20 수집 | 231 | 국가 표준 시설·수용량 | 공식 |
| 안양시 민방위 급수시설 | 안양시·공공데이터포털 | 2025-03-12 / 2026-08-22 수집 | 46 | 대응자원 맥락 | 공식 |
| 전국 민방위 급수시설(안양 필터) | 행정안전부·LocalData | 2026-08-20 수집 | 71 | 국가 자원 맥락 | 공식 |
| 안양시 수방자재 | 안양시·공공데이터포털 | 2025-12-30 / 2026-08-22 수집 | 33 | 대응자원 맥락 | 공식 |
| 안양시 AED | 경기도·공공데이터포털 | 2025-12-22 / 2026-08-20 수집 | 305 | 시민 AED 119-first 정보 | 공식 |
| 주민등록 인구 | 안양시 | 2026-07-31 / 2026-08-22 수집 | 31개 동, 562,143명 | 대피 수요 | 공식 총계 + 위치 anchor는 가정 |
| 보행 네트워크 | OpenStreetMap | 2026-08-20 snapshot | 16,745 nodes / 19,439 edges | shortest-path 비용 | 공식 공공데이터 아님, ODbL |

인구는 수요, 대피시설은 용량 제약, 도로 그래프는 이동 비용, 급수·수방자재·AED는 대응 맥락으로 역할을 분리한다. 모든 자료를 하나의 solver에 넣는다고 주장하지 않는다.

## 4쪽 | 4D 시스템 구조

4D의 네 번째 축은 시간이다. 각 frame에서 다음 상태를 다시 계산한다.

`HazardState(t) → RoadState(t) → FacilityState(t) → DemandState(t) → ResourceState(t)`

가정 영역이 바뀌면 영향 수요를 계산하고, 도로 폐쇄 여부와 시설 availability/capacity를 반영해 대피 배정을 다시 수행한다. 이것은 화면 애니메이션이 아니라 시간별 계산 상태의 재산출이다. hazard는 `ADMIN_SCENARIO`로 표시된 행정 가정이며 공식 재난 예보가 아니다.

## 5쪽 | 용량 제약 대피와 Scenario A/B

정확 엔진은 capacity-constrained min-cost flow를 사용한다. 수요가 공급되고, 이용 가능한 시설은 유효 수용량만큼만 받으며, 도보 네트워크 최단거리 비용을 최소화한다. 수용량이 부족하거나 연결되지 않는 수요는 unserved로 명시한다. 따라서 `assigned + unserved = total_demand`, 시설 배정은 수용량 이하, 폐쇄 시설 배정은 0이라는 불변식을 검사한다.

고정 A/B 데모는 동일한 영역에서 고부하 대피시설 하나를 사용할 수 없게 만든다. 결과는 available shelters `-1`, assignment cost `+1,001,955.9 m`, assigned/unserved 변화 `0`이다. 즉 이번 가정에서는 수요를 모두 배정할 여력이 남았지만, 같은 수요가 훨씬 더 먼 시설로 이동해 시스템 효율과 여유가 악화됐다.

## 6쪽 | AI 후보 선별과 exact 검증

많은 조합을 모두 exact 계산하면 행정 검토 비용이 커진다. AI는 exact reference engine이 만든 160개 simulated administrative scenario의 결과 순위를 학습한다. 입력은 solver 실행 후 값이 아닌 28개 pre-solver feature이며, 표준화 Ridge를 사용한다.

작업 흐름은 `많은 후보 → Ridge shortlist → top-K exact 검증 → authoritative result`다. AI는 최종 판단자가 아니다. 모든 선택 결과의 최종 표시값은 exact simulator에서 재검증하고, AI 추정값과 exact 값을 별도로 감사한다. 이 구조는 AI를 쓰면서도 운영상 오류 전파를 제한하는 안전장치다.

| 모델 | 데이터 | feature | validation Spearman | OOD Spearman | Recall@20 | 역할 | 최종 검증 |
|---|---|---:|---:|---:|---:|---|---|
| standardized Ridge | 160 simulated administrative scenarios | 28 pre-solver | 0.977020 | 0.964430 | validation 0.95 / OOD 0.85 | 관리자 shortlist | exact top-K 필수 |

Ridge는 CPU-friendly, 재현 가능, 해석 가능한 모델이며 이 corpus에서 강한 ranking 결과를 보였다. 다만 assignment-cost P95와 OOD 약점 때문에 운영 자동판정이 아니라 DEMO_ONLY로 남겼다.

## 7쪽 | 구현 화면과 사용자 흐름

관리자 데모는 `/admin?demo=1`에서 고정 competition preset으로 시작한다. ① 가정 영역을 확인하고 ② timeline을 움직여 도로·시설·수요 상태 변화를 본다. ③ A/B에서 시설 outage의 결과를 비교한다. ④ AI 대규모 시나리오 선별에서 후보 지원상태와 ranking을 확인하고 ⑤ top-K exact verification 결과를 확인한다. provenance 패널과 export는 입력·가정·결과의 출처를 함께 남긴다.

시민 화면은 AED와 공공시설 조회 중심이며, 행정 What-if를 시민 공식 안내로 변환하지 않는다. 지도 타일 요청이 실패해도 vector/data 패널과 주요 레이아웃이 유지된다.

## 8쪽 | 검증과 정량 성능

검증 데이터에서 exact 시뮬레이션 우선순위와 AI 순위의 Spearman 상관은 validation `0.977020`, OOD `0.964430`이었다. validation Recall@20은 `0.95`, OOD Recall@20은 `0.85`다. 이는 정확도 97.7%가 아니라 순위 상관 지표다.

동일 실행의 N=20 측정에서 전체 exact는 `32,167.964 ms`, AI 선별+상위 5개 exact 재검증은 `18,033.545 ms`로 약 `1.78배` 빨랐다. 100개 후보 실브라우저 AI+exact 대표 측정은 `24.889 s`이며 hosted SLA나 실시간 보장이 아니다. N=1000은 측정하지 않았고 extrapolation하지 않는다. 최종 검증은 Python 91, Vitest 5, Playwright 18 passed, production build와 release audit PASS다.

## 9쪽 | 안전성·한계·데이터 신뢰성

검증 결과가 부족한 지형 기반 street-level flood path는 `TERRAIN_C`로 분류하고 제품에서 제외했다. flood mode는 행정자가 입력한 가정 침수영역에 따른 도로·시설·대피 영향 What-if일 뿐 침수 예측이나 침수심 예측이 아니다. AI는 `DEMO_ONLY`이며 exact 검증이 필수다. 인구 총계는 공식값이지만 위치는 원자료에 동 경계가 없어 simulated allocation anchor다. 지역 224건과 국가 필터 231건은 provenance를 보존하며 중복 합산하지 않는다.

데이터 최신성은 각 source의 기준일·수집일·hash와 함께 관리한다. OSM 타일은 외부 의존성이므로 실패할 수 있으나 demo는 중립 지도와 데이터 패널로 fail-safe 동작한다. 이 제한은 숨기지 않고 제출 패키지와 시연 설명에 포함한다.

## 10쪽 | 확장성과 기대효과

단기적으로 공식 hazard feed, 동 경계 polygon, 추가 municipal resource, 배포 패키징과 성능 최적화를 연결한다. 중기적으로 다른 지자체, 지역 재난계획, 공식 도로 통제·시설 상태를 지원한다. 장기적으로 관측 재난 데이터와 검증된 hazard model을 확보했을 때만 해당 기능을 검토한다.

기대효과는 재난을 자동 예측한다는 약속이 아니라, 행정자가 “무엇이 바뀌면 어디가 병목이 되는가”를 같은 기준으로 비교하고 기록하는 시간과 판단 품질의 개선이다. SAFE-Twin의 핵심은 일반 지도나 단일 AI가 아니라 안양 공공데이터, 시간 변화, 용량 제약, A/B, AI shortlist와 exact verification을 하나의 감사 가능한 workflow로 연결한 점이다.
