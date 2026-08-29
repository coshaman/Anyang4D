import { useMemo, useState } from "react";
import { buildEventShareUrl, createEventPlan, decodeEventPlan, type EventPlan, type EventPoint } from "./eventPlan";
import { EventVideo } from "./EventVideo";
import { FloorPlanCanvas } from "./FloorPlanCanvas";
import { MapView } from "./MapView";
import { buildQrImageUrl } from "./qr";

function demoPlan(): EventPlan {
  const plan = createEventPlan("SAFE-Twin 행사 대피 안내", "안양대학교 강당", "INDOOR");
  plan.groups[0] = { ...plan.groups[0], start: { x: 120, y: 90 }, exit: { x: 600, y: 100 }, assembly: { x: 700, y: 400 }, route: [{ x: 120, y: 90 }, { x: 360, y: 90 }, { x: 600, y: 100 }, { x: 700, y: 400 }] };
  return plan;
}

const facilityLabels = { AED: "AED", EXTINGUISHER: "소화기", STAIRS: "계단", RESTRICTED_ZONE: "출입 제한 구역" };

export function EventPublicPage({ plan: suppliedPlan }: { plan?: EventPlan }) {
  const plan = useMemo(() => {
    if (suppliedPlan) return suppliedPlan;
    const token = new URLSearchParams(window.location.search).get("plan");
    if (token) { try { return decodeEventPlan(token); } catch { /* fall through to a safe demo */ } }
    return demoPlan();
  }, [suppliedPlan]);
  const [groupId, setGroupId] = useState(plan.groups[0]?.id ?? "A");
  const [qrFailed, setQrFailed] = useState(false);
  const group = plan.groups.find((item) => item.id === groupId) ?? plan.groups[0];
  const shareUrl = buildEventShareUrl(plan);
  const points = [group?.start, group?.exit, group?.assembly, ...plan.optionalFacilities.map((item) => item.point)].filter((point): point is EventPoint => Boolean(point));
  const outdoorFacilities = plan.outdoorFacilities ?? [];
  const outdoorRoute = group?.outdoorRoute ?? [];
  const outdoorGeometry = group?.outdoorStart && group?.outdoorExit ? [group.outdoorStart, ...outdoorRoute, group.outdoorExit, ...(group.outdoorAssembly ? [group.outdoorAssembly] : [])] : [];
  return <main className="event-public" aria-label="공개 행사 대피 안내">
    <p className="section-kicker">행사 대피 안내</p>
    <h1>{plan.name}</h1>
    <p className="event-venue">{plan.venue} · {plan.representation === "INDOOR" ? "실내 도면" : "야외 지도"}</p>
    <p className="event-public-notice">이 안내 경로는 행사 운영자가 지정한 경로입니다. 현장 안내요원의 지시를 우선하세요.</p>
    <label className="admin-field">현재 구역<select aria-label="현재 위치/구역" value={groupId} onChange={(event) => setGroupId(event.target.value)}>{plan.groups.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
    <section className="event-map-panel" aria-label="행사 대피 지도">
      {plan.representation === "INDOOR" ? <FloorPlanCanvas width={800} height={500} imageUrl={plan.floorPlan?.mimeType === "application/pdf" ? undefined : plan.floorPlan?.dataUrl} points={points} route={group?.route ?? []} onPointAdd={() => undefined} /> : <div className="event-outdoor-map"><MapView facilities={[]} onSelect={() => undefined} currentLocation={null} eventSafetyPoints={outdoorFacilities} walkingRoute={outdoorGeometry.length > 1 ? { geometry: outdoorGeometry, origin: group!.outdoorStart!, destination: group!.outdoorAssembly ?? group!.outdoorExit! } : null} /><p>야외 행사 지도 · 운영자 지정 경로 {outdoorRoute.length}점</p></div>}
      <dl className="event-route-facts">
        <div><dt>현재 위치/구역</dt><dd>{group?.name ?? "미지정"}</dd></div>
        <div><dt>출구</dt><dd>{group?.exit || group?.outdoorExit ? "지정됨" : "미지정"}</dd></div>
        <div><dt>집결지</dt><dd>{group?.assembly || group?.outdoorAssembly ? "지정됨" : "미지정"}</dd></div>
      </dl>
      {group?.routeLabel && <p className="event-route-label">안내 경로 · {group.routeLabel}</p>}
      {(plan.optionalFacilities.length > 0 || outdoorFacilities.length > 0) && <ul className="event-facilities" aria-label="행사 안전 지점">{[...plan.optionalFacilities, ...outdoorFacilities].map((item, index) => <li key={`${item.kind}-${index}`}>{facilityLabels[item.kind]}{item.label ? ` · ${item.label}` : ""}</li>)}</ul>}
    </section>
    <section className="event-actions"><h2>비상 행동</h2><ul>{plan.emergencyInstructions.map((item) => <li key={item}>{item}</li>)}</ul>{plan.organizerContact && <p>행사 문의 · {plan.organizerContact}</p>}<a className="primary-emergency" href="tel:119">☎ <span><strong>위급 시 119 신고</strong><small>위치를 설명하고 안내를 따르세요.</small></span></a></section>
    <section className="event-share"><h2>이 안내 공유</h2>{qrFailed && <p className="qr-fallback" role="status">QR 이미지를 불러오지 못했습니다. 아래 공개 URL을 복사하거나 브라우저로 열어 공유하세요.</p>}<img src={buildQrImageUrl(shareUrl)} onError={() => setQrFailed(true)} alt="행사 대피 안내 공개 URL QR 코드" width="240" height="240" style={qrFailed ? { display: "none" } : undefined} /><code>{shareUrl}</code><button type="button" onClick={() => void navigator.clipboard?.writeText(shareUrl)}>공개 URL 복사</button></section>
    <EventVideo plan={plan} groupId={plan.videoConfig?.groupId ?? groupId} />
  </main>;
}
