# 심사위원 예상 질문과 답변

## 왜 AI가 필요한가?

exact 계산은 신뢰할 수 있지만 많은 시나리오 조합을 모두 계산하면 비용이 커진다. AI는 160개 exact-labeled simulated scenario에서 배운 28개 pre-solver feature로 우선 검토 후보를 줄이고, 최종 결과는 exact가 검증한다.

## Ridge면 너무 단순한 것 아닌가?

CPU 친화적이고 재현 가능하며 계수 해석이 가능한 모델을 선택했다. validation ranking Spearman 0.977020, OOD 0.964430을 보였지만 cost-tail 한계 때문에 운영 자동판정으로 승격하지 않고 DEMO_ONLY로 고정했다.

## 실제 재난을 예측하는가?

아니다. 관리자 입력의 `ADMIN_SCENARIO` What-if를 계산한다. 공식 hazard forecast나 terrain-derived 침수 예측을 주장하지 않는다.

## 안전디딤돌과 뭐가 다른가?

기능을 폄하하지 않고 역할로 구분한다. 일반적인 알림·정보·시설 조회와 달리 SAFE-Twin은 도로·시설 availability·capacity·수요를 시간 frame별로 재계산하고 A/B와 exact assignment를 비교하는 관리자 workflow다.

## 인구 위치가 실제 위치인가?

아니다. 2026-07-31 공식 동별 총계 562,143명은 보존했고, 원본에 동 polygon이 없어 좌표는 simulated allocation anchor다.

## 대피소 224와 231은 왜 다른가?

224는 안양시 municipal 목록, 231은 행정안전부/LocalData의 엄격한 안양 필터 국가 표준 목록이다. crosswalk는 24 exact, 147 strong, 53 local-only, 60 national-only로 관계를 기록하되 운영 목록으로 합산하지 않는다.

## 왜 flood prediction을 포기했나?

최근 NGII 자료를 검토했지만 현재 증거로 street-level 품질을 방어할 수 없어 TERRAIN_C와 DROP으로 고정했다. 검증되지 않은 지형 결과를 안전 기능처럼 연결하지 않는 것이 더 신뢰할 수 있는 개발 결정이다.

## AI가 틀리면 어떻게 하나?

AI estimate는 authoritative가 아니다. shortlist의 최종 표시값은 exact simulator로 재검증하고, 지원 범위를 벗어난 후보는 unsupported 상태로 남긴다.

## 왜 exact engine이 필요한가?

capacity-constrained min-cost flow의 conservation과 폐쇄시설 0 배정 같은 불변식을 직접 보장하고, AI가 학습하지 못한 시나리오에서도 감사 가능한 기준값을 제공하기 때문이다.

## 1.78배면 AI 효과가 작은 것 아닌가?

주장 범위를 좁혀야 한다. N=20 동일 실행에서 전체 exact 32,167.964ms 대비 hybrid 18,033.545ms였다. 이는 약 1.78배이며, AI가 최종 안전판정을 대체한다는 주장이 아니다.

## 100개 분석에 25초면 느린 것 아닌가?

100개는 행정 batch screening이고 실시간 시민 기능이 아니다. 대표 실브라우저 측정은 24.889초이며, 발표에서는 고정 후보를 먼저 준비하고 한 번의 exact verification을 실제로 수행하는 흐름을 쓴다.

## 실제 지자체에서 쓸 수 있나?

현재는 competition-ready bounded prototype이다. 공식 hazard feed, 동 경계, 공식 도로·시설 상태, 배포 packaging을 단계적으로 추가하고 각 단계마다 검증한다.

## OSM이 끊기면 어떻게 하나?

외부 tile 실패를 가정한 브라우저 테스트에서 vector/data panel과 layout이 유지됐다. OSM은 ODbL attribution을 지키며, tile 가용성을 공식 hazard truth로 취급하지 않는다.

## 데이터 최신성은?

각 manifest에 기준일·수집일·hash를 보존한다. 인구 기준일은 2026-07-31, national shelter/water와 OSM snapshot은 2026-08-20, local extracts는 2026-08-22 수집이다. 실시간이라고 부르지 않는다.

## 다른 도시에도 적용 가능한가?

canonical city state와 provider adapter를 분리했기 때문에 구조적으로 가능하다. 다만 도시별 시설 정의·동 경계·공식 source를 새로 검증해야 하며 자동 이식이라고 약속하지 않는다.
