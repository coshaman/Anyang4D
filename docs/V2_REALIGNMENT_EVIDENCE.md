# SAFE-Twin Anyang V2 realignment evidence

검증 기준일: 2026-08-29  
작업 브랜치: `codex/v2-realignment`

## 제품 경계

SAFE-Twin V2는 시민, 행사 안내, 관리자(재난 시뮬레이션·고급 분석)가 같은 MapLibre 지도 코어를 공유한다. SOLWEIG/Tmrt/UTCI, PhysicsNeMo/FNO 미기후, Cool AI route, 공식 태양 그림자, 물리 기반 홍수 깊이·예측, 공식 Rain-aware route, 토지피복 의존 Nature route는 제품 기능으로 노출하지 않는다.

## 구현 증거

- 2D/3D 지도: `MapView.tsx`의 MapLibre `fill-extrusion`; 높이 우선순위는 OSM `height` → `building:levels × 3m` → 평면 fallback이며 provenance를 분리한다.
- 4D: 시나리오 프레임에서 hazard, 폐쇄 도로, 시설 load/capacity, `대피 수요 이동` 흐름을 MapLibre source로 갱신하고 0/10/20/30분 타임라인을 제공한다.
- 시민 경로: OSM 그래프 기반 경로 geometry, 출발/목적지 marker, 거리·예상 시간·fit bounds·오류 상태와 대안 경로를 제공한다.
- 경로 성능: OSM payload와 parsed graph를 프로세스 수명 동안 캐시하고, 전체 k-shortest 탐색 대신 bounded 우회 edge probe로 두 번째 실제 후보를 찾는다.
- 행사 계획: 야외/실내 선택, PNG/JPEG/SVG/PDF 입력, image-local 도면 pan/zoom, A/B/C 구역별 노드·수동 경로, 선택적 AED/소화기/계단/제한구역, 조직자 연락처를 지원한다. 야외 안전 지점은 위경도 좌표로 별도 저장한다.
- 야외 행사 경로: 실내 이미지 좌표와 분리된 위경도 시작·출구·경로를 MapLibre 클릭으로 지정하고, 집결지까지 연결한다. AED·소화기·계단·출입 제한 지점은 라벨이 있는 MapLibre 점 레이어로 주최자 지도와 공개 지도에 표시하며, 결정론적 영상 좌표에도 전달한다.
- 행사 편집: 그룹별 경로 라벨과 시작·출구·집결지 및 선택 안전 지점 삭제/재지정을 제공한다.
- 공개 행사: `/event/{slug}`에서 구역, 출구, 집결지, 비상 행동, 연락처, QR-ready URL, 실내 도면/야외 MapLibre 지도와 AED·소화기·계단·출입 제한 지점 목록을 제공한다.
- 영상: 동일 `EventPlan`에서 6장면 1920×1080 canvas를 만들고 play/pause/restart/fullscreen/WebM export를 제공한다. 실내 도면 업로드는 영상 배경으로 렌더링하고, 야외 계획은 지도형 배경을 사용한다. WebM export는 설정된 장면 길이의 전체 storyboard를 가상 타임라인으로 순회해 녹화한다. 영상용 A/B/C 구역, 제목, 로고, 장면 길이, 문자 크기, 캡션/브라우저 음성 미리듣기 프리셋을 저장하며, TTS는 재생 시 장면별 브라우저 편의 기능으로만 동작한다. WebM은 화면과 자막만 authoritative export다.
- 관리자: `행사 안내`, `재난 시뮬레이션`, `고급 분석` workspace와 지도 클릭 기반 도로 선택을 제공한다. 시설 마커를 클릭하면 해당 시설이 편집 대상으로 선택되고 현재 용량을 편집값에 불러온다. 고급 분석의 AI 선별은 모든 관리자 화면에서 접근 가능하며, bounded timeout/진단 상태와 모델 미준비 오류를 표시한다.
- 공개 훈련 복구: `trainingDemo.ts`의 0/10/20/30분 정적 사전계산 프레임을 첫 화면에 사용한다. 관리자 시나리오 목록/프레임 API는 초기 렌더에서 호출하지 않으며, 사용자가 요청한 서버 새로고침만 8초 제한으로 실행하고 실패 시 정적 프레임을 유지한다. 공개 훈련 범례에 영향 영역·통행 제한·수요 흐름·시설 부하 의미를 표시한다.
- 실내 PDF: 업로드한 PDF data URL을 브라우저 PDF object로 실제 편집 surface 아래에 렌더링하고, 그 위에 시작/출구/집결지 마커와 편집 가능한 route polyline을 겹친다. 브라우저 PDF viewer가 지원하지 않는 경우 원본 열기 안내를 표시한다.
- 공개 readiness 복구: `/readyz`는 필수 runtime artifact 존재만 확인하는 캐시된 경량 probe를 사용하고, 그래프·solver·AI 모델 상세 검증은 `/api/release/readiness`로 분리한다. 콜드 스타트 첫 health probe에서 대형 파일 파싱이 발생하지 않는다.
- 관리자 AI bounded recovery: 고급 분석 UI는 후보 생성 수와 별개로 상위 3개만 exact 검증하도록 요청해 응답 시간을 bounded하게 유지하고, 실패/timeout 시 사용자에게 상태를 명시한다.

## 실행한 검증

- `npx vitest run --pool=threads --maxWorkers=1`: 10 files, 37 tests passed.
- `pytest tests/test_release_readiness.py tests/test_production_container.py -q`: 3 passed, 1 skipped; 경량 `/readyz` probe와 상세 readiness 분리를 확인했다.
- `npm run build`: TypeScript와 Vite build passed.
- `pytest tests/test_goal4a_api.py tests/test_goal2_data.py tests/test_goal7a_flow.py -q`: 13 passed.
- `pytest tests/test_goal4a_assignment.py tests/test_goal4a_state_engine.py tests/test_goal4b_data.py tests/test_goal5a_contracts.py tests/test_goal5a_model.py tests/test_goal5a_screening_api.py -q`: 19 passed (도로/시설 상태 변경과 exact assignment 영향 포함).
- Playwright `v2-map.spec.ts` 및 `v2-event-public.spec.ts`: desktop targeted run에서 3D source/layer 1개와 행사 3개가 통과했다. 공개 행사 페이지, QR target 실제 재접속, 장면 전환, EBML WebM download, 실내 image-local 경로 그리기, 야외 MapLibre 경로·AED 공개 전환을 포함한다.
- Playwright 시민 경로 및 preview smoke: desktop 단일 worker에서 경로 geometry 렌더링과 large-text/offline/미리보기 흐름 통과.
- Playwright `v2-4d-source.spec.ts`: phone/desktop 2 tests passed; timeline이 hazard와 `evacuation-flow` source를 변경한다.
- Playwright 관리자 핵심 기능: phone/desktop 8 tests passed; timeline, A/B, export, road/facility authoring, AI separation을 포함한다.
- Playwright production config: 최신 `dist`를 FastAPI same-origin runtime으로 기동한 뒤 no-mock `production-recovery.spec.ts` 2 tests passed; `/healthz`, `/readyz`, real facilities, citizen route, training frame, admin readiness/AI path를 확인했다. MapLibre worker 의존 자산도 번들되어 `maplibre-gl-shared` 404가 재발하지 않음을 확인했다.
- production recovery 재검증: 최신 정적 훈련/PDF 변경 후 same-origin FastAPI runtime에서 `production-recovery.spec.ts` 2 tests passed (17.2s); `/readyz`, AED endpoint, 시민 도보 geometry, 정적 훈련 화면, 관리자 exact/AI 경로를 확인했다.
- production event route check: same-origin runtime에서 `/event-admin`과 `/event/{slug}` 모두 200 및 공개 행사 heading 렌더를 확인했다. 관리자 AI bounded 요청은 단일 worker smoke에서 1/1 passed (50.6s).
- 자동 초안 단위 검증: indoor L-route 생성/편집 계약과 public 4-frame overlay 계약을 포함해 targeted Vitest 10 tests passed.
- `scripts/check_anti_slop.py`: passed.
- `scripts/check_secrets.py`: passed.

## 화면 증거

검토한 산출물:

- `artifacts/evals/v2/screenshots/citizen-390.png`
- `artifacts/evals/v2/screenshots/citizen-768.png`
- `artifacts/evals/v2/screenshots/citizen-1280.png`
- `artifacts/evals/v2/screenshots/citizen-3d-1280.png`
- `artifacts/evals/v2/screenshots/event-public-video-1280.png`
- `artifacts/evals/v2/screenshots/event-public-1440.png`
- `artifacts/evals/v2/screenshots/admin-4d-0min-1280.png`
- `artifacts/evals/v2/screenshots/admin-4d-10min-1280.png`
- `artifacts/evals/v2/screenshots/admin-4d-20min-1280.png`
- `artifacts/evals/v2/screenshots/admin-4d-30min-1280.png`
- `artifacts/evals/v2/screenshots/event-organizer-indoor-1280x720-desktop.png`

4D 상태 캡처를 시각 검토한 결과, 0/10/20/30분에서 hazard 범위, 통행 제한 선, 시설/배정 지표가 각각 달라졌고 지도 레이어와 관리자 패널이 함께 렌더링되었다.
실내 행사 안내 캡처에서는 단계형 행사 설정, 실내 도면 편집 surface, image-local 경로 polyline, 구역/영상 프리셋이 함께 보인다.

## 제한사항 및 배포 게이트

- 공개 HTTPS 배포는 검증하지 않았다. `artifacts/final/deployment-smoke.json`의 `public_https=false`, `public_url=null`이 현재 authoritative evidence다. 공개 URL/QR resolve를 주장하려면 호스팅 인증 후 동일 최신 커밋으로 smoke test를 다시 실행해야 한다.
- Docker/실제 컨테이너 재실행은 현재 호스트에서 Docker 엔진을 사용할 수 없어 이번 변경에서 재검증하지 않았다.
- 관리자 4D source-change Playwright 테스트 2개와 관리자 기능 Playwright 테스트 8개는 단일 worker 실행에서 통과했다. 병렬 실행은 이 Windows 환경의 Chromium native process 자원 문제로 불안정하므로 릴리스 검증은 단일 worker 기준으로 고정한다.
- `/admin?demo=1`은 0/10/20/30분의 네 상태 시각화 preset을 명시적으로 선택한다. 4D source-change 테스트 2개는 수정 후 통과했다.
- QR 이미지는 외부 QR 이미지 제공자가 차단될 때 공개 URL fallback을 표시한다. URL 자체는 페이지 내부에서 확인 가능하다.
- 실내 경로는 운영자 수동 지정이며 법정 안전·소방 적합성 인증이 아니다. 대형 floor-plan asset은 URL token 크기 제한을 고려해 로컬 브라우저 범위로 취급한다.

이번 V2 realignment 변경의 마지막 커밋은 현재 브랜치의 최신 커밋으로 확인한다. 공개 배포와 관리자 Chromium 안정화가 확인되기 전에는 전체 목표를 완료로 표시하지 않는다.
