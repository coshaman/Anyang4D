# 제출 패키지 manifest

## REQUIRED

| 분류 | 경로 | 포함 이유 |
|---|---|---|
| 제품 | `apps/`, `services/`, `scripts/start_demo.ps1`, `scripts/smoke_demo.ps1` | 실행 가능한 prototype |
| 제출 본문 | `docs/SUBMISSION_10PAGE_CONTENT_MASTER.md` | 10페이지 원고 |
| 심사 보조 | `docs/SUBMISSION_FIGURE_PLAN.md`, `docs/COMPETITION_SCORING_MAP.md`, `docs/JUDGE_QA.md`, `docs/DEMO_SCRIPT_3MIN.md` | 발표·심사 대응 |
| 증거 | `artifacts/evals/release/`, `artifacts/evals/performance/`, `artifacts/evals/submission/` | 재현·검증 |
| 그림 | `artifacts/competition/submission-selected/` | 제출용 실제 capture |
| 데이터 | `data/manifests/data_manifest.json`, lawful processed derivatives | provenance와 demo 입력 |
| 고지 | `THIRD_PARTY_NOTICES.md`, `docs/RELEASE_DATA_POLICY.md` | ODbL/BSD/제공기관 조건 |
| 최종 감사 | `artifacts/final/public-release-manifest.json`, `artifacts/final/final-privacy-audit.json`, `artifacts/final/final-claim-audit.json`, `artifacts/final/deployment-smoke.json` | 공개 릴리스 범위와 주장·개인정보 검증 |

## OPTIONAL

`docs/COMPETITION_ONE_PAGE.md`, `docs/COMPETITION_TECHNICAL_EVIDENCE.md`, `docs/COMPETITION_CLAIMS_MATRIX.md`, model card, source crosswalk와 evaluation scripts. 공식 양식이 요구하는 경우에만 첨부한다.

## DO_NOT_SHIP

- `docs/` 안의 raw NGII DXF와 raw NGII DEM ZIP/IMG
- provider-auth gated raw files, `.env`, API keys, secrets, local caches, Playwright traces
- 실제 시민 위치·실시간 인구·공식 emergency forecast·관측 피해 labels
- terrain-derived flood depth 또는 citizen hazard-routing output
- 심사에 필요하지 않은 실패한 historical model artifact
- `artifacts/final/private-source/`와 공식 서식 원본에 포함된 비공개 입력

패키지 전 검사는 파일 크기, license/provenance, secret, absolute Windows path, raw research artifact를 확인한다. NGII 파일은 local competition machine audit용으로만 유지한다.

## 현재 제출 선택물 size check

| 선택물 | 측정 크기 |
|---|---:|
| 10페이지 content master | 9,479 bytes |
| figure plan | 2,368 bytes |
| scoring map | 2,320 bytes |
| judge Q&A | 4,027 bytes |
| 3분 demo script | 2,356 bytes |
| evidence consistency JSON | 2,935 bytes |
| claim audit JSON | 2,502 bytes |
| selected screenshots 7장 합계 | 2,235,960 bytes |

이 표는 2026-08-24 로컬 workspace에서 측정한 현재 산출물 크기이며, 공식 제출 파일 크기 제한 자체는 사람 체크리스트에서 공고와 대조한다.
