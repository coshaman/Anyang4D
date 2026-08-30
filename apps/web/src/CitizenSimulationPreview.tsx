import { useEffect, useMemo, useState } from "react";
import { MapView } from "./MapView";
import { facilities, type Facility } from "./realData";
import { API_BASE, readJsonResponse } from "./api";
import { describeTrainingFrame, trainingDemoFrames, trainingDemoScenario, type TrainingDemoScenario } from "./trainingDemo";

type Scenario = TrainingDemoScenario;
type Frame = {
  hazard: { geometry: Record<string, unknown> | null; label: string | null; provenance: string };
  roads: { changed_count: number; changed: Array<{ a: [number, number]; b: [number, number]; reason?: string }> };
  facilities: Array<{ facility_id: string; load: number; available: boolean }>;
  available_shelter_count: number;
  assignment: { evacuation_demand: number; assigned: number; unserved: number; average_assigned_travel_distance_m: number | null };
  evacuation_flow?: Array<{ demand_node_id: string; shelter_id: string; assigned_demand: number; load_ratio: number; geometry: { type: "LineString"; coordinates: number[][] } }>;
  terrain_authorized: boolean;
  citizen_guidance_authorized: boolean;
  computation_status: string;
};

export function CitizenSimulationPreview({ onBack }: { onBack: () => void }) {
  const [scenarios, setScenarios] = useState<Scenario[]>([trainingDemoScenario]);
  const [scenario, setScenario] = useState<Scenario | null>(trainingDemoScenario);
  const [frame, setFrame] = useState<Frame | null>(trainingDemoFrames[0]);
  const [timeIndex, setTimeIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!scenario) return;
    const minute = scenario.frame_times[timeIndex] ?? scenario.frame_times[0] ?? 0;
    setFrame(trainingDemoFrames[minute] ?? trainingDemoFrames[0]);
  }, [scenario, timeIndex]);

  async function refreshFromServer() {
    if (!scenario) return;
    const minute = scenario.frame_times[timeIndex] ?? 0;
    const endpoint = `${API_BASE}/admin/goal4a/scenarios/${scenario.scenario_id}/frames/${minute}`;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(endpoint, { signal: controller.signal });
      setFrame(await readJsonResponse<Frame>(response, endpoint));
      setError("");
    } catch (error) {
      setError(`서버 계산값을 불러오지 못했습니다. 정적 사전계산 화면을 계속 표시합니다 · ${error instanceof Error ? error.message : "연결 실패"}`);
    } finally {
      window.clearTimeout(timeout);
    }
  }

  useEffect(() => {
    if (!playing || !scenario?.frame_times.length) return;
    const timer = window.setInterval(() => setTimeIndex((index) => (index + 1) % scenario.frame_times.length), 900);
    return () => window.clearInterval(timer);
  }, [playing, scenario]);

  const shelterFacilities = useMemo(() => facilities.filter((item: Facility) => item.category === "CIVIL_DEFENSE_SHELTER"), []);
  const time = scenario?.frame_times[timeIndex] ?? 0;
  const loadById = useMemo(() => {
    const simulatedLoad = frame?.facilities[0]?.load;
    const firstShelter = shelterFacilities[0];
    return firstShelter && simulatedLoad !== undefined ? { [firstShelter.id]: simulatedLoad } : {};
  }, [frame, shelterFacilities]);

  return <main className="simple-page citizen-training-page">
    <button className="back-button" type="button" onClick={onBack}>← 시민 화면</button>
    <p className="section-kicker">훈련 화면</p>
    <h1>재난 상황 미리보기</h1>
    <p className="lead">실제 재난 안내가 아닌, 관리자 가정 시나리오의 계산 결과를 시민용으로 단순하게 확인합니다.</p>
    <div className="training-warning" role="note"><strong>훈련/가정 시나리오</strong><span>공식 재난문자와 현장 안내를 우선하세요. 이 화면은 대피 지시나 안전 보장을 제공하지 않습니다.</span></div>
    {error && <p className="error-message" role="alert">{error}</p>}
    {scenarios.length > 0 && <label className="admin-field">시나리오<select value={scenario?.scenario_id ?? ""} onChange={(event) => { setScenario(scenarios.find((item) => item.scenario_id === event.target.value) ?? null); setTimeIndex(0); }}><option value="" disabled>시나리오 선택</option>{scenarios.map((item) => <option key={item.scenario_id} value={item.scenario_id}>{item.scenario_id === trainingDemoScenario.scenario_id ? "정적 공개 프리뷰 · 4개 프레임" : item.title}</option>)}</select></label>}
    {scenario && <>
      <p className="provenance-line">공개 훈련 모드 · 정적 사전계산값 우선 <button className="text-button" type="button" onClick={() => void refreshFromServer()}>서버 계산값 새로고침</button></p>
      {frame && <section className="training-now" aria-label="현재 시뮬레이션 해석"><p className="section-kicker">현재 시뮬레이션</p><h2>{time}분 · {time === 0 ? "초기 영향" : time === 10 ? "통행 제한 확산" : time === 20 ? "대피소 병목 증가" : "대피소 가용성 저하"}</h2><p>{describeTrainingFrame(frame, time)}</p><dl><div><dt>영향 영역</dt><dd>지도 붉은 영역</dd></div><div><dt>통행 상태</dt><dd>{frame.roads.changed_count}개 제한</dd></div><div><dt>시설 상태</dt><dd>{frame.available_shelter_count}곳 가용</dd></div><div><dt>대피 결과</dt><dd>{frame.assignment.unserved.toLocaleString()}명 미배정</dd></div></dl></section>}
      <section className="training-legend" aria-label="훈련 오버레이 범례"><strong>지도에서 읽는 법</strong><span className="legend-item legend-hazard">붉은 영역: 훈련 영향 영역</span><span className="legend-item legend-closure">주황 선: 통행 제한 도로</span><span className="legend-item legend-flow">굵은 파란 선: 대피 수요 흐름</span><span className="legend-item legend-facility">원 크기/색: 시설 부하·가용 여부</span></section>
      <div className="training-controls"><button className="secondary-button" type="button" onClick={() => setPlaying((value) => !value)}>{playing ? "일시정지" : "재생"}</button><label htmlFor="training-time">시간 {time}분</label><input id="training-time" type="range" min="0" max={Math.max(0, scenario.frame_times.length - 1)} value={timeIndex} onChange={(event) => setTimeIndex(Number(event.target.value))} aria-label="훈련 시나리오 시간" /></div>
      <MapView facilities={shelterFacilities} onSelect={() => undefined} currentLocation={null} hazardGeometry={frame?.hazard.geometry} hazardLabel={frame?.hazard.label} changedRoads={frame?.roads.changed} facilityLoads={loadById} facilityLoadRatios={loadById} evacuationFlow={frame?.evacuation_flow} />
      {frame && <section className="training-results" aria-label="훈련 계산 결과"><h2>{scenario.title}</h2><p className="provenance-line">계산 상태 · {frame.computation_status} · {frame.hazard.provenance}</p><dl><div><dt>대피 수요</dt><dd>{frame.assignment.evacuation_demand.toLocaleString()}명</dd></div><div><dt>배정</dt><dd>{frame.assignment.assigned.toLocaleString()}명</dd></div><div><dt>미배정</dt><dd>{frame.assignment.unserved.toLocaleString()}명</dd></div><div><dt>가용 대피소</dt><dd>{frame.available_shelter_count}곳</dd></div><div><dt>통행 제한</dt><dd>{frame.roads.changed_count}개</dd></div></dl><p className="notice-text">이 결과는 가정 조건의 계산값입니다. terrain 기반 시민 hazard routing과 공식 대피 지시는 연결되어 있지 않습니다.</p></section>}
    </>}
    {!scenario && !error && <p className="loading-state">훈련 시나리오를 불러오는 중입니다…</p>}
  </main>;
}
