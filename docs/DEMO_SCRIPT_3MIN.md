# SAFE-Twin Anyang 3분 데모 스크립트

대상 화면: `/admin?demo=1`. 100개 후보 계산을 발표 중 기다리며 완료된 것처럼 말하지 않는다. 고정 demo preset과 실제 exact verification을 중심으로 진행한다.

## 0:00–0:30 | 문제와 데이터

“SAFE-Twin은 시민 알림 앱이 아니라 행정 What-if 도구입니다. 안양시 공식 인구 31개 동 562,143명, municipal/national 시설 자료, 자원 맥락과 보행 graph를 provenance와 함께 연결했습니다. 인구는 수요, 시설은 capacity, 도로는 이동 비용으로 역할이 다릅니다.”

## 0:30–1:15 | 4D timeline

timeline을 중간 frame으로 이동한다. “4D의 네 번째 축은 시간입니다. 이 화면은 애니메이션만 재생하는 것이 아니라 frame마다 가정 영역, 도로 availability, 시설 상태, 영향 수요를 다시 계산합니다. 지금 보는 hazard는 공식 예보가 아니라 관리자 입력 시나리오입니다.”

## 1:15–1:50 | Shelter outage A/B

고정 A/B variant를 연다. “동일한 영역에서 고부하 대피시설 하나를 닫았습니다. available shelters는 1개 감소했고 총 assignment cost는 1,001,955.9m 증가했습니다. assigned/unserved는 변하지 않았습니다. 수용 여력은 남았지만 같은 수요를 더 먼 시설로 보내 resilience가 악화된 사례입니다.”

## 1:50–2:35 | AI screening

AI panel을 연다. “많은 조합을 exact로 모두 계산하기 전에 Ridge AI가 160개 simulated administrative scenario와 28개 pre-solver feature를 바탕으로 우선순위를 선별합니다. validation Spearman은 0.977020, OOD는 0.964430입니다. 이것은 accuracy 97.7%가 아니라 순위 상관입니다. AI는 DEMO_ONLY입니다.”

## 2:35–2:55 | Exact verification

top-K exact verification을 실행/확인한다. “선별 후보의 최종 수치는 exact simulator가 다시 계산합니다. AI 추정과 exact 결과를 나란히 감사하고, authoritative badge는 exact 결과에만 붙습니다.”

## 2:55–3:00 | 마무리

“SAFE-Twin은 재난을 예언하는 서비스가 아니라, 안양의 실제 공공데이터와 가정 시나리오를 사용해 무엇이 바뀌면 대피 시스템이 어떻게 달라지는지 비교하는 4D 행정 의사결정 지원 서비스입니다.”
