# Goal 6B 독립 self-review

## A. 공공데이터 심사자

- strongest point: 224/231 시설을 합산하지 않고 local/national provenance와 crosswalk 관계를 보존하며, 인구·시설·네트워크의 계산 역할을 분리했다.
- biggest weakness: 일부 local/resource 자료는 solver의 직접 제약이 아니라 context다.
- likely deduction: 안양 데이터가 장식용이라는 오해가 생길 수 있다.
- exact revision made: 10페이지 3쪽에 수요·capacity·network·resource 역할표와 공식/가정 구분을 추가했다.

## B. AI/technical 심사자

- strongest point: validation/OOD ranking 지표와 N=20 동일 실행 속도, exact top-K 필수 구조를 함께 제시했다.
- biggest weakness: 1000 후보를 측정하지 않았고 cost-tail error가 높다.
- likely deduction: AI의 운영 일반화·실시간성 점수.
- exact revision made: `AI_SURROGATE_B`/`DEMO_ONLY`, N=1000 미측정, 24.889초 batch limitation을 본문·QA·manifest에 명시했다.

## C. 지방자치단체/공공안전 심사자

- strongest point: AI와 지형 기반 hazard를 시민 공식 안내에 연결하지 않고 exact verifier를 둔 보수적 경계.
- biggest weakness: simulated spatial population anchors와 공식 realtime hazard feed 부재.
- likely deduction: 현장 운영 readiness.
- exact revision made: 9쪽에서 공식 총계와 simulated anchor를 분리하고 10쪽 roadmap에 동 경계·hazard feed를 검증 조건으로 명시했다.

## D. 회의적 제품 심사자

- strongest point: 실제 browser capture, A/B, export, accessibility, fail-safe tile behavior와 재현 artifact가 있다.
- biggest weakness: cold start 15.380초, 대표 100-candidate batch 24.889초.
- likely deduction: 시연 중 대기와 운영 비용.
- exact revision made: 3분 script는 100개 실시간 대기를 전제로 하지 않고 고정 demo와 실제 exact verification을 중심으로 구성했다. latency는 숨기지 않았다.
