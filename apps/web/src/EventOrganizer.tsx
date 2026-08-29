import { useState } from "react";
import { addEventNode, addRoutePoint, createEventPlan, updateEventGroup, type EventPlan, type EventPoint, type EventRepresentation } from "./eventPlan";
import { FloorPlanCanvas } from "./FloorPlanCanvas";

export function EventOrganizer({ onPreview, onBack }: { onPreview: (plan: EventPlan) => void; onBack?: () => void }) {
  const [step, setStep] = useState(1);
  const [name, setName] = useState("");
  const [venue, setVenue] = useState("");
  const [representation, setRepresentation] = useState<EventRepresentation>("OUTDOOR");
  const [plan, setPlan] = useState<EventPlan>(() => createEventPlan("", "", "OUTDOOR"));
  const [groupId, setGroupId] = useState("A");
  const [nodeKind, setNodeKind] = useState<"start" | "exit" | "assembly" | "AED">("start");
  const [drawingRoute, setDrawingRoute] = useState(false);
  const activeGroup = plan.groups.find((group) => group.id === groupId) ?? plan.groups[0];
  function updatePlan(next: EventPlan) { setPlan(next); }
  function loadFloorPlan(file: File | undefined) {
    if (!file || !["image/png", "image/jpeg", "image/svg+xml", "application/pdf"].includes(file.type)) return;
    const reader = new FileReader();
    reader.onload = () => updatePlan({ ...plan, floorPlan: { mimeType: file.type as "image/png" | "image/jpeg" | "image/svg+xml" | "application/pdf", dataUrl: String(reader.result), width: 800, height: 500 } });
    reader.readAsDataURL(file);
  }
  function placePoint(point: EventPoint) { updatePlan(drawingRoute ? addRoutePoint(plan, groupId, point) : addEventNode(plan, groupId, nodeKind, point)); }
  function preview() { onPreview({ ...plan, name, venue, representation, slug: name.trim().toLowerCase().replace(/\s+/g, "-") || "event" }); }
  return <main className="event-organizer" aria-label="행사 대피안내 만들기"><button className="back-button" type="button" onClick={onBack}>← 관리자 홈</button><p className="section-kicker">행사 안내</p><h1>행사 대피안내 만들기</h1><p className="lead">행사 운영자가 지정한 안내 경로로 참가자용 대피자료를 만듭니다.</p><p className="event-safety-notice">본 서비스는 대피 안내자료 제작을 돕는 도구입니다. 실제 행사 운영 전 시설 안전관리자·행사 책임자가 경로를 확인하세요.</p>{step === 1 && <section className="event-step"><h2>1. 행사 정보</h2><label className="admin-field">행사명<input aria-label="행사명" value={name} onChange={(event) => setName(event.target.value)} placeholder="예: 안양 해커톤" /></label><label className="admin-field">행사 장소<input aria-label="행사 장소" value={venue} onChange={(event) => setVenue(event.target.value)} placeholder="예: 안양대학교 강당" /></label><button className="secondary-button" type="button" onClick={() => { setPlan(createEventPlan(name, venue, representation)); setStep(2); }}>다음</button></section>}{step >= 2 && <section className="event-step"><h2>2. 장소 표현</h2><label className="form-check"><input type="radio" aria-label="야외/캠퍼스 지도" checked={representation === "OUTDOOR"} onChange={() => setRepresentation("OUTDOOR")} />야외/캠퍼스 지도</label><label className="form-check"><input type="radio" aria-label="실내 도면" checked={representation === "INDOOR"} onChange={() => setRepresentation("INDOOR")} />실내 도면</label><button className="secondary-button" type="button" onClick={() => setStep(3)}>다음</button><button className="primary-button" type="button" onClick={preview}>계획 미리보기</button></section>}{step >= 3 && <section className="event-step"><h2>3. 구역과 안내 경로</h2><div className="admin-controls"><label>구역<select aria-label="행사 구역" value={groupId} onChange={(event) => setGroupId(event.target.value)}>{plan.groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}</select></label><label>표시<select aria-label="안내 지점 종류" value={nodeKind} onChange={(event) => setNodeKind(event.target.value as typeof nodeKind)}><option value="start">참가자 시작 구역</option><option value="exit">비상 출구</option><option value="assembly">집결지</option><option value="AED">AED</option></select></label><button className="secondary-button" type="button" onClick={() => setDrawingRoute((value) => !value)}>{drawingRoute ? "경로 그리기 종료" : "경로 그리기"}</button></div>{representation === "INDOOR" && <><label className="admin-field">실내 도면 파일<input aria-label="실내 도면 파일" type="file" accept="image/png,image/jpeg,image/svg+xml,application/pdf" onChange={(event) => loadFloorPlan(event.target.files?.[0])} /></label>{plan.floorPlan && <p role="status">도면 파일이 선택되었습니다.</p>}<FloorPlanCanvas width={800} height={500} imageUrl={plan.floorPlan?.mimeType === "application/pdf" ? undefined : plan.floorPlan?.dataUrl} points={[activeGroup.start, activeGroup.exit, activeGroup.assembly].filter((point): point is EventPoint => Boolean(point))} route={activeGroup.route} onPointAdd={placePoint} /></>}{representation === "OUTDOOR" && <p className="event-map-hint">야외 지도에서는 기존 OSM 보행 경로를 참고하고, 최종 안내 경로는 운영자가 확인합니다.</p>}<button className="primary-button" type="button" onClick={preview}>계획 미리보기</button></section>}</main>;
}
