# 제출 그림 계획

| 그림 | 원본 | crop/표시 | 캡션 | 지원 주장 | 목표 쪽 |
|---|---|---|---|---|---:|
| Fig. 1 시민 화면 | `artifacts/competition/screenshots/01-citizen-map.png` | 전체, 상단 중심 | 시민은 AED·공공시설 정보와 기본 지도 기반을 사용한다. | 시민/관리자 분리 | 2, 7 |
| Fig. 2 관리자 시작 | `03-admin-demo-opening.png` | 전체 | 고정 demo preset에서 시간축 행정 시나리오를 시작한다. | working prototype, 4D | 4, 7 |
| Fig. 3 4D 중간 frame | `04-admin-timeline-mid-state.png` | timeline·metrics 영역 | frame 변경에 따라 도로·시설·수요 상태와 배정 결과가 재계산된다. | 시간축 계산 | 4, 7 |
| Fig. 4 Scenario A/B | `05-scenario-ab.png` | A/B 결과 영역 | 고부하 시설 하나의 outage가 가용시설과 총 assignment cost를 바꾼다. | originality, exact A/B | 5 |
| Fig. 5 AI와 exact | `06-ai-screening-and-exact-verification.png` | AI shortlist와 exact badge | AI는 후보를 선별하고 top-K는 exact로 검증한다. | AI safety architecture | 6, 8 |
| Fig. 6 provenance | `08-provenance-panel.png` | source/provenance panel | 공식·가정·simulated allocation의 출처를 구분한다. | public-data quality | 3, 9 |

## 그림 제작 규칙

원본은 실제 브라우저 capture이며 core request를 mock하지 않았다. 각 그림은 장식이 아니라 표의 수치·workflow·경계 중 하나를 증명한다. 최종 PDF에서는 글자가 읽히도록 Fig. 5와 Fig. 6을 2단 편집하지 않고 폭을 우선한다. `09-citizen-large-text.png`는 accessibility appendix 선택 그림으로 둔다.

## 시스템 architecture figure specification

```text
안양 공식 데이터 + OSM snapshot
              ↓
       canonical city state
              ↓
       4D scenario engine
              ↓
 road graph + demand + capacity
              ↓
      exact min-cost flow
              ↓
          A/B What-if

scenario candidates → Ridge surrogate → top-K → exact verification
                                           AI ≠ final authority
```

## Demo walkthrough figure specification

`① 가정영역 설정 → ② 시간 frame에서 도로·시설 상태 변경 → ③ exact 대피수요 재배정 → ④ A/B 비교 → ⑤ AI 후보 다수 선별 → ⑥ top-K exact 검증`
