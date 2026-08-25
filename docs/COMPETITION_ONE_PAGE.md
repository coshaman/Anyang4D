# SAFE-Twin Anyang — one-page technical summary

## 문제

행정 담당자가 안양의 공공데이터와 가정 시나리오를 한 화면에서 비교하고, 변화의 계산 결과를 빠르게 검토할 수 있어야 합니다.

## 데이터

국가 필터링 대피시설 231개, 급수 맥락 71개, AED 305개와 안양시 공식 31개 동·562,143명 인구를 사용합니다. 지역 자료 224개 대피시설, 46개 급수시설, 33개 수방자재 기록은 국가 자료와 분리 보존합니다.

## 4D simulation

시간별 가정 영역, 도로 폐쇄, 시설 폐쇄/용량, 참여율을 exact deterministic engine이 계산하고, NetworkX min-cost flow로 대피 수요를 시설에 배정합니다. 이는 행정 훈련/what-if이지 실제 재난 예보가 아닙니다.

## AI screening

160개 simulated administrative scenario와 28개 pre-solver feature로 Ridge surrogate를 학습했습니다. Validation ranking Spearman은 0.977020, OOD Spearman은 0.964430입니다.

## Exact verification

AI는 우선 검토 후보만 선별합니다. 표시되는 최종 값은 반드시 exact simulator로 재검증되며 AI 추정치와 exact 결과를 함께 감사할 수 있습니다. 운영 자동판정은 허용하지 않습니다.

## 시민/관리자 분리

`/admin?demo=1`은 관리자 demo surface이고, 시민 화면은 공공시설 조회와 기본 보행 네트워크 확인만 제공합니다. 시민 화면에는 AI 선별·행정 hazard·terrain flood output이 연결되지 않습니다.

## Measured result

20개 후보에서 전체 exact 계산 32,167.964 ms 대비 AI 선별+상위 5개 exact 검증 18,033.545 ms를 같은 실행에서 측정해 약 1.78배 빨랐습니다. 100개 후보 실제 브라우저 데모의 대표 측정값은 AI+exact 24.889초이며, 이는 로컬 Windows CPU의 일회성 측정값이지 실시간 SLA가 아닙니다.
