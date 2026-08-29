# SAFE-Twin Anyang V2 Product Realignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild SAFE-Twin Anyang around a shared 2.5D/3D map, visible 4D simulation, event evacuation authoring, public event sharing, and deterministic WebM guidance while removing unsupported claims.

**Architecture:** Extend the existing MapLibre/React frontend with typed shared map layers and separate citizen, event, simulation, and advanced-admin workspaces. Keep the exact FastAPI scenario/routing backend; keep event plans client-side and share structured plans through URL tokens with explicit large-asset limits.

**Tech Stack:** React, TypeScript, MapLibre GL, SVG/canvas, MediaRecorder/WebM, existing FastAPI/NetworkX APIs, Vitest, pytest, Playwright.

**Spec:** `docs/superpowers/specs/2026-08-29-safe-twin-anyang-v2-design.md`

## Global Constraints

- Do not display unsupported microclimate, terrain-flood, solar-shadow, Cool AI, or Nature-route features as pending or available.
- Use MapLibre fill-extrusion and provenance `OSM_HEIGHT`, `DERIVED_LEVEL_HEIGHT`, or `UNKNOWN_HEIGHT`; approximate height is never official.
- Keep exact scenario outputs and OSM routing assets; do not draw one evacuation line per resident.
- Indoor routes are manual operator-approved image-local polylines; the system never infers indoor-safe routes.
- Event routes are organizer-designated guidance, not certified safe routes.
- Use deterministic client-side video; no generative AI video, paid TTS, or required server ffmpeg.
- Test behavior before implementation, run the failing test, then minimal implementation and regression tests.
- Visually inspect 390×844, 768×1024, 1280×720, and 1440×900 required screens.

---

### Task 1: Shared 2.5D/3D map foundation

**Files:**
- Modify: `apps/web/src/MapView.tsx`
- Modify: `apps/web/src/App.tsx`
- Modify: `apps/web/src/styles.css`
- Test: `apps/web/src/MapView.test.tsx`
- Test: `tests/e2e/v2-map.spec.ts`

**Interfaces:** `MapView` accepts `buildings`, `viewMode`, and `onViewModeChange`; building properties expose `height_m` and `height_provenance`. It emits stable source IDs `buildings`, `facilities`, `walking-route`, `scenario-hazard`, `scenario-closures`, and `evacuation-flow`.

- [ ] Write a failing unit test asserting building GeoJSON keeps OSM height first, derives levels at 3.0m, and labels missing height `UNKNOWN_HEIGHT`.
- [ ] Run `npm test -- MapView.test.tsx`; confirm failure because the building layer contract is absent.
- [ ] Add the typed building normalization and fill-extrusion layer with 2D/3D toggle, pitch, rotation, north reset, and readable facility layers.
- [ ] Run the focused unit test and `npm run build`; confirm both pass.
- [ ] Add Playwright behavior assertions for source/layer visibility and camera state at desktop/mobile widths.
- [ ] Capture and inspect citizen normal-map and 3D screenshots at all four required viewports.
- [ ] Commit the map foundation.

### Task 2: Visible 4D scenario and aggregated evacuation flow

**Files:**
- Modify: `apps/web/src/CitizenSimulationPreview.tsx`
- Modify: `apps/web/src/AdminSimulator.tsx`
- Modify: `apps/web/src/MapView.tsx`
- Modify: `apps/web/src/styles.css`
- Test: `apps/web/src/ScenarioLayers.test.tsx`
- Test: `tests/e2e/v2-simulation.spec.ts`

**Interfaces:** A frame maps to hazard GeoJSON, changed-road GeoJSON, facility load properties, and `evacuation-flow` features with `demand_node_id`, `shelter_id`, `assigned_demand`, and `load_ratio`. The timeline uses four distinct times `[0,10,20,30]` when supplied by the scenario.

- [ ] Write a failing test that computes layer data for two frames and asserts hazard, closure, facility-load, and flow source data differ.
- [ ] Run the focused test and observe the missing flow/layer behavior.
- [ ] Implement frame-to-layer adapters and a map-dominant timeline with play, pause, scrub, current time, and reduced-motion static arrows.
- [ ] Use line width for assigned demand and marker size/fill for facility load; label the feature `대피 수요 이동`.
- [ ] Run unit/build checks and Playwright assertions for actual MapLibre source differences, not only text.
- [ ] Capture t0, later-frame, and A/B screenshots at required viewports.
- [ ] Commit the 4D visualization.

### Task 3: Event plan model and outdoor/indoor authoring

**Files:**
- Create: `apps/web/src/eventPlan.ts`
- Create: `apps/web/src/eventPlan.test.ts`
- Create: `apps/web/src/EventOrganizer.tsx`
- Create: `apps/web/src/FloorPlanCanvas.tsx`
- Modify: `apps/web/src/App.tsx`
- Modify: `apps/web/src/styles.css`
- Test: `tests/e2e/v2-event-authoring.spec.ts`

**Interfaces:** `createEventPlan`, `encodeEventPlan`, `decodeEventPlan`, `addEventNode`, `updateEventGroup`, and `addRoutePoint` are pure functions. `EventOrganizer` accepts `onPreview(plan)` and returns a validated `EventPlan`; `FloorPlanCanvas` emits image-local `Point` values.

- [ ] Write failing tests for event validation, group-specific routes, URL-safe round-trip, and image-local point preservation.
- [ ] Run tests and confirm the pure helpers/components are absent.
- [ ] Implement the wizard: event name/address, outdoor/indoor choice, participant/start, exit, assembly, optional safety facilities, groups A/B/C, and manual route drawing.
- [ ] Accept PNG/JPEG/SVG and first-page PDF when browser support permits; show an actionable unsupported-file error.
- [ ] Add organizer notice exactly: `본 서비스는 대피 안내자료 제작을 돕는 도구입니다. 실제 행사 운영 전 시설 안전관리자·행사 책임자가 경로를 확인하세요.`
- [ ] Run unit/build and Playwright behavior tests for drawing/edit/delete and group-specific routes.
- [ ] Capture organizer and indoor floor-plan screenshots at all required viewports.
- [ ] Commit the event authoring workflow.

### Task 4: Public event page, QR, and deterministic video

**Files:**
- Create: `apps/web/src/EventPublicPage.tsx`
- Create: `apps/web/src/EventVideo.tsx`
- Create: `apps/web/src/qr.ts`
- Create: `apps/web/src/eventVideo.test.ts`
- Modify: `apps/web/src/App.tsx`
- Modify: `apps/web/src/styles.css`
- Test: `tests/e2e/v2-event-public.spec.ts`

**Interfaces:** `/event/:slug?plan=<token>` decodes to `EventPlan`; `buildEventShareUrl(plan, origin)` returns the public URL; `EventVideo` exposes `play`, `pause`, `restart`, `exportWebm`, and `fullscreen` controls and emits `data-scene-index`.

- [ ] Write failing tests for public-plan decode, QR matrix containing the public URL payload, six scene advancement, route visibility in scene 4/5, and nonempty WebM success/error handling.
- [ ] Run tests and confirm the missing public/video behavior.
- [ ] Implement the public event page with event name, current group/location, exit, assembly, emergency actions, optional AED/contact, and concise organizer notice.
- [ ] Implement QR as deterministic SVG/canvas output without network or paid dependency.
- [ ] Implement 1920×1080 logical SVG/canvas storyboard, preview, controls, fullscreen, reduced-motion mode, and MediaRecorder WebM export.
- [ ] Run unit/build and Playwright tests for public URL, QR resolution, scene changes, and export bytes.
- [ ] Capture public event, video preview, and QR screenshots at all required viewports.
- [ ] Commit public sharing and video.

### Task 5: Admin workspace restructure and unsupported-feature removal

**Files:**
- Create: `apps/web/src/AdminWorkspaces.tsx`
- Modify: `apps/web/src/AdminSimulator.tsx`
- Modify: `apps/web/src/App.tsx`
- Modify: `apps/web/src/styles.css`
- Test: `apps/web/src/App.test.tsx`
- Test: `tests/e2e/v2-admin.spec.ts`

**Interfaces:** `/admin` renders three workspace labels `행사 안내`, `재난 시뮬레이션`, and `고급 분석`; event workspace owns event/video, simulation owns scenario/timeline/A-B, advanced owns closures/capacity/resources/AI/provenance.

- [ ] Write failing tests that normal citizen text contains none of `ADMIN_SCENARIO`, `exact solver`, `edge ID`, `AI screening`, or `capacity override`, and admin workspaces expose the three intended sections.
- [ ] Run tests and confirm current UI violates the vocabulary/workspace assertions.
- [ ] Move existing controls into workspace tabs/sections, replace opaque edge-ID editing with map click selection where the backend permits, and keep advanced diagnostics out of citizen mode.
- [ ] Remove unsupported-feature labels, routes, and “coming soon” references from product UI while preserving research artifacts.
- [ ] Run all frontend tests, build, and no-mock existing admin P0 tests.
- [ ] Capture advanced-admin and simulation screenshots at all required viewports.
- [ ] Commit the workspace restructure.

### Task 6: Full visual/functional audit and release

**Files:**
- Create: `tests/e2e/v2-release-audit.spec.ts`
- Create: `artifacts/evals/v2/README.md`
- Modify: `docs/DEPLOYMENT.md`

- [ ] Add behavior tests for 3D layer, real route geometry with origin/destination and two candidates where available, four frame source changes, road/facility edits, floor-plan drawing, event public URL/QR, video route scene, and citizen jargon absence.
- [ ] Run the new suite against a production FastAPI-served build and retain screenshots for all required screens and viewports.
- [ ] Inspect every screenshot for clipped text, inaccessible controls, blank maps, unreadable 3D markers, and false safety claims; fix the source and rerun the affected test.
- [ ] Run `npm test`, `npm run build`, `.venv\\Scripts\\python.exe -m pytest -q`, `npm run check:anti-slop`, and `npm run check:secrets`, recording exact results.
- [ ] Run the public URL no-mock suite after deployment and verify release identity, `/healthz`, `/readyz`, route, event page, video export, and admin flows in the same latest deployment.
- [ ] Write the final V2 evidence report with restored features, removals, replacements, screenshots, tests, public result, and limitations.
- [ ] Commit and push the release evidence.
