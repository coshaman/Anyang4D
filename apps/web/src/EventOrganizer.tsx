import { useState } from "react";
import { addEventNode, addOutdoorFacility, addOutdoorNode, addOutdoorRoutePoint, addRoutePoint, clearEventNode, createEventPlan, removeLastEventFacility, removeLastOutdoorRoutePoint, removeLastRoutePoint, type EventPlan, type EventPoint, type EventRepresentation, type OutdoorPoint } from "./eventPlan";
import { FloorPlanCanvas } from "./FloorPlanCanvas";
import { MapView } from "./MapView";

const instructionOptions = ["뛰지 마세요", "엘리베이터를 사용하지 마세요", "안내요원의 지시에 따르세요", "위험지역으로 되돌아가지 마세요", "위급 시 119에 신고하세요"];
type NodeKind = "start" | "exit" | "assembly" | "AED" | "EXTINGUISHER" | "STAIRS" | "RESTRICTED_ZONE";

export function EventOrganizer({ onPreview, onBack }: { onPreview: (plan: EventPlan) => void; onBack?: () => void }) {
  const [step, setStep] = useState(1);
  const [name, setName] = useState("");
  const [venue, setVenue] = useState("");
  const [organizerContact, setOrganizerContact] = useState("");
  const [representation, setRepresentation] = useState<EventRepresentation>("OUTDOOR");
  const [plan, setPlan] = useState<EventPlan>(() => createEventPlan("", "", "OUTDOOR"));
  const [groupId, setGroupId] = useState("A");
  const [nodeKind, setNodeKind] = useState<NodeKind>("start");
  const [drawingRoute, setDrawingRoute] = useState(false);
  const [selectedInstructions, setSelectedInstructions] = useState(() => createEventPlan("", "", "OUTDOOR").emergencyInstructions);
  const [videoTitle, setVideoTitle] = useState("");
  const [sceneDurationSeconds, setSceneDurationSeconds] = useState(4);
  const [textSize, setTextSize] = useState<"standard" | "large" | "compact">("standard");
  const [narration, setNarration] = useState<"caption" | "tts-preview">("caption");
  const [videoGroupId, setVideoGroupId] = useState("A");
  const [logoDataUrl, setLogoDataUrl] = useState<string | undefined>();
  const activeGroup = plan.groups.find((group) => group.id === groupId) ?? plan.groups[0];
  function updatePlan(next: EventPlan) { setPlan(next); }
  function loadFloorPlan(file: File | undefined) {
    if (!file || !["image/png", "image/jpeg", "image/svg+xml", "application/pdf"].includes(file.type)) return;
    const reader = new FileReader();
    reader.onload = () => updatePlan({ ...plan, floorPlan: { mimeType: file.type as "image/png" | "image/jpeg" | "image/svg+xml" | "application/pdf", dataUrl: String(reader.result), width: 800, height: 500 } });
    reader.readAsDataURL(file);
  }
  function loadLogo(file: File | undefined) {
    if (!file || !file.type.startsWith("image/")) return;
    const reader = new FileReader();
    reader.onload = () => setLogoDataUrl(String(reader.result));
    reader.readAsDataURL(file);
  }
  function placePoint(point: EventPoint) { updatePlan(drawingRoute ? addRoutePoint(plan, groupId, point) : addEventNode(plan, groupId, nodeKind, point)); }
  function placeOutdoorPoint(point: OutdoorPoint) {
    if (drawingRoute) { updatePlan(addOutdoorRoutePoint(plan, groupId, point)); return; }
    if (nodeKind === "start" || nodeKind === "exit" || nodeKind === "assembly") updatePlan(addOutdoorNode(plan, groupId, nodeKind, point));
    else updatePlan(addOutdoorFacility(plan, nodeKind, point));
  }
  const outdoorRoute = activeGroup.outdoorRoute ?? [];
  const outdoorGeometry = activeGroup.outdoorStart && activeGroup.outdoorExit ? [activeGroup.outdoorStart, ...outdoorRoute, activeGroup.outdoorExit, ...(activeGroup.outdoorAssembly ? [activeGroup.outdoorAssembly] : [])] : [];
  const activeRouteLength = representation === "OUTDOOR" ? outdoorRoute.length : activeGroup.route.length;
  function preview() { onPreview({ ...plan, name, venue, representation, emergencyInstructions: selectedInstructions, organizerContact: organizerContact.trim() || undefined, slug: name.trim().toLowerCase().replace(/\s+/g, "-") || "event", logoDataUrl, videoConfig: { title: videoTitle.trim(), sceneDurationSeconds, textSize, narration, logoDataUrl, ...(videoGroupId !== "A" ? { groupId: videoGroupId } : {}) } }); }
  return <main className="event-organizer" aria-label="행사 대피안내 만들기">
    <button className="back-button" type="button" onClick={onBack}>← 관리자 홈</button>
    <p className="section-kicker">행사 안내</p><h1>행사 대피안내 만들기</h1>
    <p className="lead">행사 운영자가 지정한 안내 경로로 참가자용 대피자료를 만듭니다.</p>
    <p className="event-safety-notice">본 서비스는 대피 안내자료 제작을 돕는 도구입니다. 실제 행사 운영 전 시설 안전관리자·행사 책임자가 경로를 확인하세요.</p>
    {step === 1 && <section className="event-step"><h2>1. 행사 정보</h2><label className="admin-field">행사명<input aria-label="행사명" value={name} onChange={(event) => setName(event.target.value)} placeholder="예: 안양 해커톤" /></label><label className="admin-field">행사 장소<input aria-label="행사 장소" value={venue} onChange={(event) => setVenue(event.target.value)} placeholder="예: 안양대학교 강당" /></label><label className="admin-field">행사 문의 연락처<input aria-label="행사 문의 연락처" value={organizerContact} onChange={(event) => setOrganizerContact(event.target.value)} placeholder="선택: 031-000-0000" /></label><button className="secondary-button" type="button" onClick={() => { setPlan(createEventPlan(name, venue, representation)); setStep(2); }}>다음</button></section>}
    {step >= 2 && <section className="event-step"><h2>2. 장소 표현</h2><label className="form-check"><input type="radio" aria-label="야외/캠퍼스 지도" checked={representation === "OUTDOOR"} onChange={() => setRepresentation("OUTDOOR")} />야외/캠퍼스 지도</label><label className="form-check"><input type="radio" aria-label="실내 도면" checked={representation === "INDOOR"} onChange={() => setRepresentation("INDOOR")} />실내 도면</label><button className="secondary-button" type="button" onClick={() => setStep(3)}>다음</button><button className="primary-button" type="button" onClick={preview}>계획 미리보기</button></section>}
    {step >= 3 && <section className="event-step"><h2>3. 구역과 안내 경로</h2><div className="admin-controls"><label>구역<select aria-label="행사 구역" value={groupId} onChange={(event) => setGroupId(event.target.value)}>{plan.groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}</select></label><label>표시<select aria-label="안내 지점 종류" value={nodeKind} onChange={(event) => setNodeKind(event.target.value as NodeKind)}><option value="start">참가자 시작 구역</option><option value="exit">비상 출구</option><option value="assembly">집결지</option><option value="AED">AED</option><option value="EXTINGUISHER">소화기</option><option value="STAIRS">계단</option><option value="RESTRICTED_ZONE">출입 제한 구역</option></select></label><button className="secondary-button" type="button" onClick={() => setDrawingRoute((value) => !value)}>{drawingRoute ? "경로 그리기 종료" : "경로 그리기"}</button><button className="secondary-button" type="button" disabled={!activeRouteLength} onClick={() => updatePlan(representation === "OUTDOOR" ? removeLastOutdoorRoutePoint(plan, groupId) : removeLastRoutePoint(plan, groupId))}>마지막 경로점 삭제</button></div>
      {representation === "INDOOR" && <><label className="admin-field">실내 도면 파일<input aria-label="실내 도면 파일" type="file" accept="image/png,image/jpeg,image/svg+xml,application/pdf" onChange={(event) => loadFloorPlan(event.target.files?.[0])} /></label>{plan.floorPlan && <p role="status">도면 파일이 선택되었습니다.</p>}<FloorPlanCanvas width={800} height={500} imageUrl={plan.floorPlan?.mimeType === "application/pdf" ? undefined : plan.floorPlan?.dataUrl} points={[activeGroup.start, activeGroup.exit, activeGroup.assembly, ...plan.optionalFacilities.map((item) => item.point)].filter((point): point is EventPoint => Boolean(point))} route={activeGroup.route} onPointAdd={placePoint} /></>}
      {representation === "OUTDOOR" && <><div className="event-outdoor-editor"><MapView facilities={[]} onSelect={() => undefined} currentLocation={null} eventSafetyPoints={plan.outdoorFacilities} walkingRoute={outdoorGeometry.length > 1 ? { geometry: outdoorGeometry, origin: activeGroup.outdoorStart!, destination: activeGroup.outdoorAssembly ?? activeGroup.outdoorExit! } : null} onMapClick={placeOutdoorPoint} /><p className="event-map-hint">지도에서 시작 구역·출구·집결지를 지정하고, 경로 그리기를 켜서 운영자 안내 경로를 추가하세요. OSM 경로는 참고용입니다.</p></div></>}
      <label className="admin-field">경로 라벨<input aria-label="경로 라벨" value={activeGroup.routeLabel ?? ""} onChange={(event) => updatePlan({ ...plan, groups: plan.groups.map((group) => group.id === groupId ? { ...group, routeLabel: event.target.value } : group) })} placeholder="예: 북쪽 출구 → 운동장 집결지" /></label>
      <button className="secondary-button" type="button" disabled={!((nodeKind === "start" && (activeGroup.start || activeGroup.outdoorStart)) || (nodeKind === "exit" && (activeGroup.exit || activeGroup.outdoorExit)) || (nodeKind === "assembly" && (activeGroup.assembly || activeGroup.outdoorAssembly)) || (nodeKind !== "start" && nodeKind !== "exit" && nodeKind !== "assembly" && (representation === "OUTDOOR" ? plan.outdoorFacilities.some((item) => item.kind === nodeKind) : plan.optionalFacilities.some((item) => item.kind === nodeKind))))} onClick={() => (nodeKind === "start" || nodeKind === "exit" || nodeKind === "assembly") ? updatePlan(clearEventNode(plan, groupId, nodeKind)) : updatePlan(removeLastEventFacility(plan, nodeKind, representation))}>선택 지점 삭제</button>
      <fieldset className="event-instructions"><legend>영상에 표시할 비상 안내</legend>{instructionOptions.map((instruction) => <label className="form-check" key={instruction}><input type="checkbox" aria-label={instruction} checked={selectedInstructions.includes(instruction)} onChange={(event) => setSelectedInstructions((current) => event.target.checked ? [...current, instruction] : current.filter((item) => item !== instruction))} />{instruction}</label>)}</fieldset>
      <fieldset className="event-video-settings"><legend>영상 프리셋</legend><label className="admin-field">영상용 구역<select aria-label="영상용 구역" value={videoGroupId} onChange={(event) => setVideoGroupId(event.target.value)}>{plan.groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}</select></label><label className="admin-field">영상 제목<input aria-label="영상 제목" value={videoTitle} onChange={(event) => setVideoTitle(event.target.value)} placeholder="선택: 행사별 영상 제목" /></label><label className="admin-field">행사 로고<input aria-label="행사 로고" type="file" accept="image/png,image/jpeg,image/svg+xml" onChange={(event) => loadLogo(event.target.files?.[0])} /></label><label className="admin-field">장면 길이<select aria-label="장면 길이" value={sceneDurationSeconds} onChange={(event) => setSceneDurationSeconds(Number(event.target.value))}><option value={3}>3초</option><option value={4}>4초</option><option value={5}>5초</option><option value={6}>6초</option></select></label><label className="admin-field">문자 크기<select aria-label="문자 크기" value={textSize} onChange={(event) => setTextSize(event.target.value as typeof textSize)}><option value="standard">기본</option><option value="large">크게</option><option value="compact">작게</option></select></label><label className="admin-field">나레이션 모드<select aria-label="나레이션 모드" value={narration} onChange={(event) => setNarration(event.target.value as typeof narration)}><option value="caption">자막만 사용</option><option value="tts-preview">브라우저 음성 미리듣기</option></select></label><p className="field-hint">음성 미리듣기는 이 기기에서만 재생되며, WebM에는 자막과 화면만 저장됩니다.</p></fieldset>
      <button className="primary-button" type="button" onClick={preview}>계획 미리보기</button></section>}
  </main>;
}
