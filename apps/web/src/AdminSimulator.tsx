import { useEffect, useMemo, useState } from "react";
import { MapView } from "./MapView";
import { facilities, type Facility } from "./realData";
import { API_BASE } from "./api";

type Scenario = Record<string, any>;
type Frame = Record<string, any>;
const API = `${API_BASE}/admin/goal4a`;

export function AdminSimulator({ onBack, demoMode = false }: { onBack: () => void; demoMode?: boolean }) {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [frame, setFrame] = useState<Frame | null>(null);
  const [time, setTime] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [compareId, setCompareId] = useState("");
  const [comparison, setComparison] = useState<Frame | null>(null);
  const [edgeId, setEdgeId] = useState("");
  const [facilityId, setFacilityId] = useState("");
  const [capacity, setCapacity] = useState(100);
  const [status, setStatus] = useState("시나리오를 불러오는 중입니다.");
  const [resourceCount, setResourceCount] = useState<number | null>(null);
  const [resources, setResources] = useState<Scenario[]>([]);
  const [resourceId, setResourceId] = useState("");
  const [drawing, setDrawing] = useState(false);
  const [drawPoints, setDrawPoints] = useState<Array<[number, number]>>([]);
  const [newDisasterType, setNewDisasterType] = useState("FLOOD");
  const [newStart, setNewStart] = useState("2026-08-22T09:00");
  const [newEnd, setNewEnd] = useState("2026-08-22T09:30");
  const [participation, setParticipation] = useState(1);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [routeStatus, setRouteStatus] = useState("");
  const [aiScreen, setAiScreen] = useState<Scenario | null>(null);
  const [aiCandidateCount, setAiCandidateCount] = useState(100);
  const [aiStatus, setAiStatus] = useState("");
  const [readiness, setReadiness] = useState<Scenario | null>(null);
  const [modeContracts, setModeContracts] = useState<Scenario[]>([]);
  const selectedModeContract = modeContracts.find((item) => item.mode === newDisasterType);

  const shelters = useMemo(() => facilities.filter((item) => item.category === "CIVIL_DEFENSE_SHELTER" && item.latitude !== null && item.longitude !== null), []);

  async function loadScenarios() {
    try {
      const response = await fetch(`${API}/scenarios`);
      if (!response.ok) throw new Error("scenario request failed");
      const body = await response.json();
      setScenarios(body.items);
      if (!selectedId && body.items[0]) setSelectedId((demoMode && body.items.find((item: Scenario) => item.scenario_id === "anyang-general-evacuation-competition")?.scenario_id) || body.items[0].scenario_id);
      if (!compareId && demoMode && body.items.find((item: Scenario) => item.scenario_id === "anyang-general-evacuation-competition-shelter-outage")) setCompareId("anyang-general-evacuation-competition-shelter-outage");
    } catch (error) {
      setStatus(`시나리오 API 오류 · ${error instanceof Error ? error.message : "연결 실패"}`);
    }
  }

  async function loadScenario(id: string) {
    if (!id) return;
    let response: Response;
    try { response = await fetch(`${API}/scenarios/${id}`); } catch { setStatus("시나리오 API가 연결되지 않았습니다."); return; }
    const body = await response.json();
    setScenario(body);
    const firstTime = body.frame_times?.[0] ?? 0;
    setTime(firstTime);
    setStatus(`${body.title} · ${body.provenance}`);
  }

  async function loadFrame(id = selectedId, at = time) {
    if (!id) return;
    try {
      const response = await fetch(`${API}/scenarios/${id}/frames/${at}`);
      if (!response.ok) { setStatus("현재 frame을 계산하지 못했습니다."); return; }
      setFrame(await response.json());
    } catch { setStatus("frame API가 연결되지 않았습니다."); }
  }

  useEffect(() => { void loadScenarios(); }, []);
  useEffect(() => { if (!window.matchMedia) return; const media = window.matchMedia("(prefers-reduced-motion: reduce)"); const update = () => setReducedMotion(media.matches); update(); media.addEventListener?.("change", update); return () => media.removeEventListener?.("change", update); }, []);
  useEffect(() => { void fetch(`${API}/resources`).then(async (response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); }).then((body) => { setResourceCount(body.count); setResources(body.items); }).catch((error) => setStatus(`공식 자원 API 오류 · ${error instanceof Error ? error.message : "연결 실패"}`)); }, []);
  useEffect(() => { void fetch(`${API_BASE}/release/readiness`).then(async (response) => { const body = await response.json(); if (!response.ok) throw new Error(`HTTP ${response.status}`); setReadiness(body); }).catch(() => setReadiness({ status: "NOT_READY", mandatory_checks: {} })); }, []);
  useEffect(() => { void fetch(`${API_BASE}/admin/modes`).then((response) => response.json()).then((body) => setModeContracts(body.items || [])).catch(() => setModeContracts([])); }, []);
  useEffect(() => { void loadScenario(selectedId); }, [selectedId]);
  useEffect(() => { void loadFrame(selectedId, time); }, [selectedId, time]);
  useEffect(() => {
    if (!playing || !scenario?.frame_times?.length) return;
    const timer = window.setInterval(() => {
      const times: number[] = scenario.frame_times;
      setTime((current) => times[(times.indexOf(current) + 1) % times.length]);
    }, 1200);
    return () => window.clearInterval(timer);
  }, [playing, scenario]);

  async function saveScenario(next: Scenario, message: string) {
    const response = await fetch(`${API}/scenarios`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(next) });
    if (!response.ok) { setStatus("시나리오 저장에 실패했습니다."); return; }
    setScenario(next);
    setStatus(message);
    await loadScenarios();
  }

  function addKeyframe() {
    if (!scenario) return;
    const keyframes = [...(scenario.hazard_keyframes || []), { time, label: "관리자 추가 가정 영역", geometry: { kind: "polygon", coordinates: [[[126.925, 37.375], [126.955, 37.375], [126.955, 37.4], [126.925, 37.4], [126.925, 37.375]]] } }].sort((a, b) => a.time - b.time);
    void saveScenario({ ...scenario, hazard_keyframes: keyframes }, `시간 ${time}분에 가정 hazard keyframe을 추가했습니다.`);
  }

  function onMapClick(point: { latitude: number; longitude: number }) {
    if (!drawing) return;
    setDrawPoints((current) => [...current, [point.longitude, point.latitude]]);
  }

  function saveDrawnHazard() {
    if (!scenario || drawPoints.length < 3) return;
    const ring = [...drawPoints, drawPoints[0]];
    const keyframes = [...(scenario.hazard_keyframes || []), { time, label: "관리자 작성 가정 영역", geometry: { kind: "polygon", coordinates: [ring] } }].sort((a, b) => a.time - b.time);
    setDrawing(false); setDrawPoints([]);
    void saveScenario({ ...scenario, hazard_keyframes: keyframes }, `지도에서 ${time}분 가정 hazard 영역을 저장했습니다.`);
  }

  function closeRoad() {
    if (!scenario || !edgeId.trim()) return;
    const events = [...(scenario.road_closure_events || []), { start_minute: time, end_minute: scenario.frame_times.at(-1) ?? time + 10, edge_ids: [edgeId.trim()], reason: "시나리오에서 통행 제한으로 설정된 도로", provenance: "ADMIN_SCENARIO" }];
    void saveScenario({ ...scenario, road_closure_events: events }, `도로 ${edgeId}를 시나리오 통행 제한으로 설정했습니다.`);
  }

  function closeFacility() {
    if (!scenario || !facilityId) return;
    const events = [...(scenario.facility_events || []), { start_minute: time, end_minute: scenario.frame_times.at(-1) ?? time + 10, facility_id: facilityId, available: false, reason: "훈련 시나리오에서 시설 폐쇄", provenance: "ADMIN_SCENARIO" }];
    void saveScenario({ ...scenario, facility_events: events }, "시설을 훈련 시나리오에서 폐쇄했습니다.");
  }

  function overrideFacilityCapacity() {
    if (!scenario || !facilityId) return;
    const overrides = [...(scenario.capacity_overrides || []), { start_minute: time, end_minute: scenario.frame_times.at(-1) ?? time + 10, facility_id: facilityId, capacity, reason: "훈련 시나리오 용량 조정", provenance: "ADMIN_SCENARIO" }];
    void saveScenario({ ...scenario, capacity_overrides: overrides }, `시설 용량을 ${capacity}명으로 조정했습니다.`);
  }

  async function duplicateScenario() {
    if (!selectedId) return;
    const newId = `${selectedId}-copy-${Date.now()}`;
    const response = await fetch(`${API}/scenarios/${selectedId}/duplicate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ new_scenario_id: newId }) });
    if (response.ok) { await loadScenarios(); setSelectedId(newId); setStatus("시나리오를 복제했습니다."); }
  }

  async function compare() {
    if (!selectedId || !compareId) return;
    const response = await fetch(`${API}/compare`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scenario_a: selectedId, scenario_b: compareId, time_minute: time }) });
    if (response.ok) { setComparison(await response.json()); setStatus("Scenario A/B 비교를 계산했습니다."); }
  }

  async function createScenario() {
    const base = scenario || scenarios[0];
    if (!base) return;
    const id = `anyang-admin-${Date.now()}`;
    const next = { ...base, scenario_id: id, title: `안양 ${newDisasterType} 관리자 시나리오`, disaster_type: newDisasterType, start_time: new Date(newStart).toISOString(), end_time: new Date(newEnd).toISOString(), description: "훈련/가정 시나리오", provenance: "ADMIN_SCENARIO", evacuation_fraction: participation, affected_demand_ids: [], affected_demand_rule: "HAZARD_CONTAINMENT_OR_EXPLICIT_SELECTION", hazard_keyframes: [], road_closure_events: [], facility_events: [], capacity_overrides: [], resource_events: [], audit_log: [] };
    const response = await fetch(`${API}/scenarios`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(next) });
    if (response.ok) { await loadScenarios(); setSelectedId(id); setStatus("새 훈련/가정 시나리오를 저장했습니다."); }
  }

  async function exportScenario() {
    if (!selectedId) return;
    const response = await fetch(`${API}/scenarios/${selectedId}/export?time_minute=${time}`);
    if (!response.ok) return;
    const blob = new Blob([JSON.stringify(await response.json(), null, 2)], { type: "application/json" });
    const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = `${selectedId}-${time}min.json`; link.click(); URL.revokeObjectURL(link.href);
    setStatus("시나리오 요약 JSON을 내보냈습니다.");
  }

  function closeResource() {
    if (!scenario || !resourceId) return;
    const events = [...(scenario.resource_events || []), { start_minute: time, end_minute: scenario.frame_times.at(-1) ?? time + 10, resource_id: resourceId, available: false, reason: "훈련 시나리오에서 자원 사용 불가", provenance: "ADMIN_SCENARIO" }];
    void saveScenario({ ...scenario, resource_events: events }, "공식 자원 맥락을 훈련 시나리오에서 비활성화했습니다.");
  }

  async function trainingRoute() {
    if (!selectedId) return;
    const response = await fetch(`${API}/training-route`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scenario_id: selectedId, time_minute: time, origin: { latitude: 37.394, longitude: 126.956 }, destination: { latitude: 37.405, longitude: 126.97 } }) });
    const body = await response.json();
    setRouteStatus(body.status === "TRAINING_SCENARIO_ROUTE" ? `훈련 경로 ${body.distance_m}m` : body.status);
  }

  async function screenAi() {
    setAiStatus("AI 후보 생성 → AI 선별 → 상위 후보 exact 재검증 중입니다. 데모용 계산이라 수 초~수십 초 걸릴 수 있습니다.");
    try {
      const response = await fetch(`${API.replace("goal4a", "goal5a")}/screen`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ candidate_count: aiCandidateCount, top_k: 10, seed: 5 }) });
      if (!response.ok) throw new Error();
      setAiScreen(await response.json());
      setAiStatus("AI 선별 완료 · 상위 후보는 exact reference engine으로 재검증했습니다.");
    } catch { setAiStatus("AI 모델이 준비되지 않았거나 API가 연결되지 않았습니다. exact 시뮬레이터는 계속 사용할 수 있습니다."); }
  }

  function hazardForMap(geometry: any) {
    if (!geometry || geometry.kind !== "point_radius") return geometry ?? null;
    const [longitude, latitude] = geometry.center;
    const radius = Number(geometry.radius_m) / 111000;
    const coordinates = Array.from({ length: 33 }, (_, index) => { const angle = (index / 32) * Math.PI * 2; return [longitude + Math.cos(angle) * radius, latitude + Math.sin(angle) * radius]; });
    return { kind: "polygon", coordinates: [coordinates] };
  }

  const hazard = hazardForMap(frame?.hazard?.geometry);
  return <main className="admin-page" aria-label="안양 행정 4D 시나리오 시뮬레이터">
    <div className="admin-map-placeholder"><MapView facilities={shelters} onSelect={() => undefined} currentLocation={null} hazardGeometry={hazard} hazardLabel={frame?.hazard?.label} onMapClick={onMapClick} changedRoads={frame?.roads?.changed ?? []} facilityLoads={Object.fromEntries((frame?.facilities ?? []).map((item: Scenario) => [item.facility_id, item.load ?? 0]))} /></div>
    <aside className="admin-pane">
      <button className="back-button" type="button" onClick={onBack}>← 시민 화면</button>
      <p className="section-kicker">행정 What-if 엔진</p><h1>안양 4D 도시상태 시뮬레이터</h1>{demoMode && <p className="scenario-assumption" role="status">대회 데모 모드 · 30초 설명용 GENERAL_EVACUATION preset</p>}
      <div className="lab-warning"><strong>훈련/가정 시나리오</strong><span>실제 재난 안내·침수심·시민 emergency routing이 아닙니다.</span></div>
      <label className="admin-field">시나리오<select value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>{scenarios.map((item) => <option key={item.scenario_id} value={item.scenario_id}>{item.title}</option>)}</select></label>
      <p className="admin-status" role="status">{status}</p>
      {scenario && <><div className="admin-controls"><button className="secondary-button" type="button" onClick={() => setPlaying((value) => !value)}>{playing ? "일시정지" : "재생"}</button><button className="secondary-button" type="button" onClick={() => void duplicateScenario()}>복제</button><button className="secondary-button" type="button" onClick={() => void trainingRoute()}>훈련 경로 계산</button><button className="secondary-button" type="button" onClick={() => void exportScenario()}>JSON 내보내기</button></div><label className="admin-field" htmlFor="goal4a-time">현재 시간: {time}분<input id="goal4a-time" aria-label="4D 시뮬레이션 타임라인" type="range" min="0" max={scenario.frame_times.length - 1} value={scenario.frame_times.indexOf(time)} onChange={(event) => setTime(scenario.frame_times[Number(event.target.value)])} /></label><p className="scenario-assumption">재난 유형: {scenario.disaster_type} · provenance: {scenario.provenance} · 공식 비상급수 맥락: {resourceCount ?? "…"}건 · {reducedMotion ? "감소된 동작" : "일반 동작"}</p>{routeStatus && <p className="scenario-assumption">{routeStatus} · 시민 안내 아님</p>}</>}
      <section className="admin-editor" aria-label="새 시나리오 작성"><h2>새 시나리오 작성</h2><div className="admin-controls"><select aria-label="새 시나리오 재난 유형" value={newDisasterType} onChange={(event) => setNewDisasterType(event.target.value)}>{["FLOOD", "EARTHQUAKE", "FIRE", "CIVIL_DEFENSE", "GENERAL_EVACUATION"].map((type) => <option key={type}>{type}</option>)}</select><input aria-label="새 시나리오 시작" type="datetime-local" value={newStart} onChange={(event) => setNewStart(event.target.value)} /><input aria-label="새 시나리오 종료" type="datetime-local" value={newEnd} onChange={(event) => setNewEnd(event.target.value)} /><label>대피 참여율 가정<select aria-label="대피 참여율 가정" value={participation} onChange={(event) => setParticipation(Number(event.target.value))}><option value="0.25">25%</option><option value="0.5">50%</option><option value="1">100%</option></select></label></div>{selectedModeContract && <div className="mode-contract" role="note"><strong>{selectedModeContract.label} · 데이터 상태: {selectedModeContract.source_status}</strong><span>가능: {selectedModeContract.supported_calculations.join(" · ")}</span><span>지원하지 않음: {selectedModeContract.unsupported_claims.join(" · ")}</span></div>}<button className="secondary-button" type="button" onClick={() => void createScenario()}>새 훈련/가정 시나리오 저장</button></section>
      <section className="admin-editor" aria-label="시나리오 편집"><h2>관리자 편집</h2><button className="secondary-button" type="button" onClick={() => { setDrawing(true); setDrawPoints([]); }}>지도에서 hazard 영역 작성 시작</button>{drawing && <p className="scenario-assumption">지도에서 3점 이상 클릭하세요: {drawPoints.length}점 · 실제 위험지도 아님</p>}<button className="secondary-button" type="button" disabled={drawPoints.length < 3} onClick={saveDrawnHazard}>작성 영역 저장</button><button className="secondary-button" type="button" onClick={addKeyframe}>현재 시간에 hazard keyframe 추가</button><label className="admin-field">도로 edge ID<input value={edgeId} onChange={(event) => setEdgeId(event.target.value)} placeholder="예: 123-456" /><button className="secondary-button" type="button" onClick={closeRoad}>도로 통행 제한 저장</button></label><label className="admin-field">시설<select value={facilityId} onChange={(event) => setFacilityId(event.target.value)}><option value="">시설 선택</option>{shelters.slice(0, 80).map((item: Facility) => <option key={item.id} value={item.id}>{item.name || item.id}</option>)}</select></label><div className="admin-controls"><button className="secondary-button" type="button" onClick={closeFacility}>시설 폐쇄</button><input aria-label="capacity override" type="number" min="0" value={capacity} onChange={(event) => setCapacity(Number(event.target.value))} /><button className="secondary-button" type="button" onClick={overrideFacilityCapacity}>용량 저장</button></div><label className="admin-field">공식 자원 맥락<select value={resourceId} onChange={(event) => setResourceId(event.target.value)}><option value="">자원 선택</option>{resources.slice(0, 80).map((item: Scenario) => <option key={item.id} value={item.id}>{item.name || item.id}</option>)}</select><button className="secondary-button" type="button" onClick={closeResource}>자원 사용 불가 저장</button></label></section>
      {frame && <><section className="admin-metrics" aria-label="현재 frame metrics"><h2>{frame.time_minute}분 frame</h2><dl className="admin-stats"><div><dt>전체 인구</dt><dd>{frame.assignment.total_population.toLocaleString()}명</dd></div><div><dt>영향 인구</dt><dd>{frame.assignment.affected_population.toLocaleString()}명</dd></div><div><dt>대피 수요</dt><dd>{frame.assignment.evacuation_demand.toLocaleString()}명</dd></div><div><dt>배정</dt><dd>{frame.assignment.assigned.toLocaleString()}명</dd></div><div><dt>미배정</dt><dd>{frame.assignment.unserved.toLocaleString()}명</dd></div><div><dt>도달 가능</dt><dd>{frame.assignment.reachable_population.toLocaleString()}명</dd></div><div><dt>변경 도로</dt><dd>{frame.roads.changed_count}</dd></div><div><dt>가용 대피소</dt><dd>{frame.available_shelter_count}</dd></div><div><dt>병목 후보</dt><dd>{frame.assignment.bottleneck_edges?.length ?? 0}</dd></div></dl><p className="scenario-assumption">대피 참여율 가정: {(frame.assignment.evacuation_fraction * 100).toFixed(0)}% · 영향 규칙: {frame.assignment.affected_demand_rule} · 수요 provenance: {frame.demand_provenance.join(", ")} · 지형 flood path: 비활성</p></section><section className="admin-editor" aria-label="Scenario A/B 비교"><h2>Scenario A/B 비교</h2><select aria-label="Scenario B 비교 대상" value={compareId} onChange={(event) => setCompareId(event.target.value)}><option value="">비교 시나리오 선택</option>{scenarios.filter((item) => item.scenario_id !== selectedId).map((item) => <option key={item.scenario_id} value={item.scenario_id}>{item.title}</option>)}</select><button className="secondary-button" type="button" onClick={() => void compare()}>차이 계산</button>{comparison && <><p className="scenario-assumption">B−A 배정 {comparison.delta_b_minus_a.assigned}명 · 미배정 {comparison.delta_b_minus_a.unserved}명 · 여행 비용 {comparison.delta_b_minus_a.assignment_cost.toLocaleString()}m · 가용 대피소 {comparison.delta_b_minus_a.available_shelters}곳 · 변경 도로 {comparison.delta_b_minus_a.changed_roads}개</p><ul className="scenario-assumption">{(comparison.why || []).map((reason: string) => <li key={reason}>{reason}</li>)}</ul></>}</section></>}
      {demoMode && <section className="admin-editor" aria-label="AI 대규모 시나리오 선별"><h2>AI 대규모 시나리오 선별</h2><p className="scenario-assumption">후보 생성 → AI 빠른 선별 → 상위 후보 exact 재검증. 모두 SIMULATED_ADMIN_SCENARIO이며 시민 안내가 아닙니다.</p><div className="admin-controls"><label>후보 수<select aria-label="AI 후보 시나리오 수" value={aiCandidateCount} onChange={(event) => setAiCandidateCount(Number(event.target.value))}><option value="100">100</option><option value="500">500</option><option value="1000">1,000</option></select></label><button className="secondary-button" type="button" onClick={() => void screenAi()}>AI 빠른 선별</button></div>{aiStatus && <p className="admin-status" role="status">{aiStatus}</p>}{aiScreen && <><p className="scenario-assumption">{aiScreen.candidate_count.toLocaleString()}개 후보 · exact 호출 {aiScreen.exact_calls}회 · 모델 {aiScreen.model_version}</p><ol className="ai-shortlist">{aiScreen.verified_shortlist.map((item: Scenario, index: number) => <li key={item.scenario_id}><strong>#{index + 1} {item.scenario_id}</strong><span>AI 추정 미배정 {Math.round(item.estimated_unserved ?? 0).toLocaleString()}명 · exact 미배정 {item.exact_result?.unserved?.toLocaleString?.() ?? "-"}명 · {item.support_status}</span><small>주요 입력: {(item.explanation || []).slice(0, 2).map((reason: Scenario) => reason.feature).join(", ") || "없음"}</small></li>)}</ol><p className="scenario-assumption">표시 최종값은 exact reference 결과이며 AI 추정치는 별도 감사용으로 보존합니다.</p></>}</section>}
      <section className="admin-editor" aria-label="배포 진단"><h2>배포 진단</h2><p className="scenario-assumption">/api/release/readiness · {readiness?.status ?? "확인 중"}</p>{readiness?.mandatory_checks && <ul className="scenario-assumption">{Object.entries(readiness.mandatory_checks).map(([key, value]: [string, any]) => <li key={key}>{key}: {value.ready ? "READY" : `FAIL${value.error ? ` · ${value.error}` : ""}`}</li>)}</ul>}</section><p className="admin-disclaimer">가정 hazard는 실제 침수·붕괴·화재 확산을 뜻하지 않습니다. 실제 재난 시 공식 통제정보를 우선 확인하세요.</p>
    </aside>
  </main>;
}
