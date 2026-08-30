import { useEffect, useMemo, useState } from "react";
import "maplibre-gl/dist/maplibre-gl.css";
import { MapView } from "./MapView";
import { AdminSimulator } from "./AdminSimulator";
import { CitizenSimulationPreview } from "./CitizenSimulationPreview";
import { CATEGORY_LABELS, dataManifest, facilities, sourceCounts, type Category, type Facility } from "./realData";
import { API_BASE, fetchJson } from "./api";
import { EventOrganizer } from "./EventOrganizer";
import { EventPublicPage } from "./EventPublicPage";
import type { EventPlan } from "./eventPlan";

type Page = "citizen" | "simulate" | "admin" | "about" | "event" | "event-public";
type Location = { latitude: number; longitude: number };
type RouteCandidate = { candidate_index?: number; geometry: Array<Location>; destination: Location; distance_m: number; estimated_walking_minutes: number; provenance?: string };

const categoryOrder: Category[] = ["CIVIL_DEFENSE_SHELTER", "EMERGENCY_WATER", "AED"];
const center: Location = { latitude: 37.4, longitude: 126.95 };

function Provenance({ facility }: { facility: Facility }) {
  const date = facility.source_update_timestamp?.split(" ")[0] ?? "기준일 미상";
  return <p className="provenance-line"><span className="source-mark" aria-hidden="true" />공식 정보 · {facility.source_provenance || "OFFICIAL"} · {date}</p>;
}
function FacilityDetails({ facility, onRoute }: { facility: Facility; onRoute: () => void }) {
  return <section className="facility-detail" aria-label="시설 상세">
    <div className="detail-heading"><div><p className="section-kicker">{CATEGORY_LABELS[facility.category]}</p><h2>{facility.name || "시설명 미상"}</h2></div><span className="official-label">공식</span></div>
    <dl>
      <div><dt>주소</dt><dd>{facility.address || "주소 미상"}</dd></div>
      {facility.category === "CIVIL_DEFENSE_SHELTER" && <>
        <div><dt>시설 위치</dt><dd>{facility.facility_position || "미상"}</dd></div>
        <div><dt>시설 면적</dt><dd>{facility.area_m2 === null || facility.area_m2 === undefined ? "미상" : `${facility.area_m2}㎡`}</dd></div>
        <div><dt>최대 수용인원</dt><dd>{facility.capacity === null ? "미상" : `${facility.capacity.toLocaleString()}명`}</dd></div>
        <div><dt>운영 상태</dt><dd>{facility.operating_info || "확인되지 않음"}</dd></div>
      </>}
      {facility.category === "EMERGENCY_WATER" && <div><dt>시설 상태</dt><dd>{facility.operating_info || "확인되지 않음"}</dd></div>}
      {facility.category === "AED" && <div><dt>이용 정보</dt><dd>{facility.access_info || "원문에 이용 가능 시간 정보가 없습니다."}</dd></div>}
    </dl>
    {facility.category === "AED" && <div className="aed-actions"><a className="primary-emergency" href="tel:119"><span aria-hidden="true">☎</span><span><strong>119 신고</strong><small>위치 확인보다 신고가 먼저입니다.</small></span></a><p className="notice-text">AED 원문에는 좌표가 없습니다. 주소를 확인하고 현장 상황을 판단하세요.</p></div>}
    {facility.latitude !== null && facility.longitude !== null && <button className="route-button" type="button" onClick={onRoute}>기본 도보 경로 보기</button>}
    <Provenance facility={facility} />
  </section>;
}

function SimulationPreview({ onBack }: { onBack: () => void }) {
  return <CitizenSimulationPreview onBack={onBack} />;
}

function AboutData({ onBack }: { onBack: () => void }) {
  return <main className="simple-page"><button className="back-button" type="button" onClick={onBack}>← 시민 화면</button><p className="section-kicker">데이터 안내</p><h1>데이터 출처와 한계</h1><p className="lead">현재 연결된 공공데이터 기준입니다. 연결되지 않은 출처는 시설로 표시하지 않습니다.</p><section className="source-table" aria-label="데이터 출처 목록">{dataManifest.map((source) => <div className="source-row" key={source.id}><div><strong>{source.dataset_title}</strong><span>{source.provider} · {source.temporal_coverage || "기간 정보 없음"}</span><small>좌표계: {source.crs || "정보 없음"} · 이용조건: {source.license_terms || "제공기관 조건 확인"}</small><a href={source.landing_url} target="_blank" rel="noreferrer">공식 페이지</a></div><span>{source.status === "DOWNLOADED" ? `연결됨 · ${source.anyang_feature_count ?? "OSM 스냅샷"}` : "연결되지 않음"}<small>검색/수집: {source.retrieval_timestamp || "기록 없음"}</small></span></div>)}</section><p className="provenance-line"><span className="source-mark official-mark" aria-hidden="true" />원문 다운로드 시각: 2026-08-20 · OpenStreetMap © contributors</p></main>;
}

function AdminShell({ onBack }: { onBack: () => void }) {
  const [timeIndex, setTimeIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const times = [0, 5, 10, 15];
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => setTimeIndex((current) => (current + 1) % times.length), 900);
    return () => window.clearInterval(timer);
  }, [playing, times.length]);
  return <main className="admin-page"><div className="admin-map-placeholder"><MapView facilities={facilities.filter((facility) => facility.category === "CIVIL_DEFENSE_SHELTER")} onSelect={() => undefined} currentLocation={null} /></div><aside className="admin-pane"><button className="back-button" type="button" onClick={onBack}>← 시민 화면</button><p className="section-kicker">내부 검증 랩</p><h1>안양 4D 내부 시뮬레이션 랩</h1><p>시민 화면과 분리된 합성 시나리오 재생 화면입니다.</p><div className="lab-warning"><strong>합성 테스트 시나리오</strong><span>시민용 안양 홍수 결과가 아닙니다 · Level A 상대 위험도만 표시</span></div><div className="lab-controls"><button className="secondary-button" type="button" onClick={() => setPlaying((value) => !value)}>{playing ? "일시정지" : "재생"}</button><label htmlFor="lab-time">시간 {times[timeIndex]}분</label><input id="lab-time" type="range" min="0" max={times.length - 1} value={timeIndex} onChange={(event) => setTimeIndex(Number(event.target.value))} aria-label="시뮬레이션 시간" /></div><div className="lab-frame" role="img" aria-label={`합성 위험도 프레임 ${times[timeIndex]}분`}><div className="lab-grid" style={{ opacity: 0.35 + timeIndex * 0.16 }} /></div><dl className="admin-stats"><div><dt>필드</dt><dd>RELATIVE_HAZARD</dd></div><div><dt>시간</dt><dd>{times[timeIndex]}분</dd></div><div><dt>출처</dt><dd>SYNTHETIC</dd></div></dl></aside></main>;
}

export function App() {
  const initialPage: Page = window.location.pathname === "/simulate" ? "simulate" : window.location.pathname === "/admin" ? "admin" : window.location.pathname === "/event-admin" ? "event" : window.location.pathname.startsWith("/event/") ? "event-public" : window.location.pathname === "/about-data" ? "about" : "citizen";
  const [page, setPage] = useState<Page>(initialPage);
  const [category, setCategory] = useState<Category>("CIVIL_DEFENSE_SHELTER");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Facility | null>(null);
  const [largeText, setLargeText] = useState(false);
  const [location, setLocation] = useState<Location | null>(null);
  const [locationMessage, setLocationMessage] = useState("");
  const [offline, setOffline] = useState(() => typeof navigator !== "undefined" && !navigator.onLine);
  const [routeMessage, setRouteMessage] = useState("");
  const [walkingRoute, setWalkingRoute] = useState<Parameters<typeof MapView>[0]["walkingRoute"]>(null);
  const [routeCandidates, setRouteCandidates] = useState<RouteCandidate[]>([]);
  const [eventPlan, setEventPlan] = useState<EventPlan | null>(null);

  useEffect(() => {
    const update = () => setOffline(!navigator.onLine);
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    return () => { window.removeEventListener("online", update); window.removeEventListener("offline", update); };
  }, []);

  const visibleFacilities = useMemo(() => facilities.filter((facility) => facility.category === category && [facility.name, facility.address].some((value) => (value || "").toLowerCase().includes(query.toLowerCase()))), [category, query]);
  const nearby = visibleFacilities.slice(0, 5);

  function toggleLargeText() { const next = !largeText; setLargeText(next); document.documentElement.dataset.textSize = next ? "large" : "default"; }
  function locate() { if (!navigator.geolocation) { setLocationMessage("이 브라우저에서는 위치를 확인할 수 없습니다. 안양시 전체를 표시합니다."); return; } navigator.geolocation.getCurrentPosition((position) => { setLocation({ latitude: position.coords.latitude, longitude: position.coords.longitude }); setLocationMessage("현재 위치를 지도에 표시했습니다."); }, () => setLocationMessage("위치를 허용하지 않아 안양시 중심으로 표시합니다.")); }
  function selectCategory(next: Category) { setCategory(next); setSelected(null); setRouteMessage(""); setWalkingRoute(null); setRouteCandidates([]); }
  async function requestRoute() { if (selected?.latitude == null || selected.longitude == null) return; const origin = location || center; const endpoint = `${API_BASE}/routes`; try { const route = await fetchJson<RouteCandidate & { candidates?: RouteCandidate[] }>(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ origin, destination: { latitude: selected.latitude, longitude: selected.longitude } }) }, 45000, 0); const candidates = route.candidates?.length ? route.candidates : [route]; setRouteCandidates(candidates); setWalkingRoute({ geometry: candidates[0].geometry, origin, destination: candidates[0].destination }); setRouteMessage(`기본 도보 경로 · 약 ${candidates[0].distance_m.toLocaleString()}m · 예상 ${candidates[0].estimated_walking_minutes}분`); } catch (error) { setWalkingRoute(null); setRouteCandidates([]); setRouteMessage(error instanceof Error ? error.message : "서버 연결 오류 · route"); } }
  function chooseRoute(candidate: RouteCandidate) { const origin = location || center; setWalkingRoute({ geometry: candidate.geometry, origin, destination: candidate.destination }); setRouteMessage(`선택한 도보 경로 · 약 ${candidate.distance_m.toLocaleString()}m · 예상 ${candidate.estimated_walking_minutes}분`); }

  if (page === "simulate") return <SimulationPreview onBack={() => setPage("citizen")} />;
  if (page === "about") return <AboutData onBack={() => setPage("citizen")} />;
  if (page === "event") return <EventOrganizer onBack={() => setPage("citizen")} onPreview={(plan) => { setEventPlan(plan); setPage("event-public"); }} />;
  if (page === "event-public") return <EventPublicPage plan={eventPlan ?? undefined} />;
  if (page === "admin") return <AdminSimulator onBack={() => setPage("citizen")} demoMode={new URLSearchParams(window.location.search).get("demo") === "1"} />;

  return <div className="app-shell">
    <header className="topbar"><a className="brand" href="/" onClick={(event) => { event.preventDefault(); setPage("citizen"); }} aria-label="SAFE-Twin 안양 홈"><span className="brand-mark" aria-hidden="true">안</span><span>SAFE-Twin 안양</span></a><nav aria-label="주요 메뉴"><button className="nav-link active" type="button">시민 화면</button><button className="nav-link" type="button" onClick={() => setPage("event")}>행사 안내 만들기</button><button className="nav-link" type="button" onClick={() => setPage("admin")}>관리자 시뮬레이터</button></nav><button className="text-toggle" type="button" onClick={toggleLargeText} aria-pressed={largeText}>{largeText ? "기본 글씨" : "큰 글씨"}</button></header>
    <main className="main-layout"><div className="content-column"><div className="status-banner" role="status"><strong>공식 데이터 기준</strong><span>대피소 {sourceCounts.CIVIL_DEFENSE_SHELTER}곳 · 급수시설 {sourceCounts.EMERGENCY_WATER}곳 · AED {sourceCounts.AED}곳</span></div>{offline && <div className="offline-banner" role="status">오프라인 · 저장된 정보 2026-08-20 20:33</div>}<div className="heading-row"><div><p className="eyebrow">안양 재난 대응</p><h1>안양 재난 대응 지도</h1><p className="intro">현재 연결된 공공데이터 기준으로 필요한 시설을 찾고 기본 도보 경로를 확인하세요.</p></div><button className="location-button" type="button" onClick={locate}><span aria-hidden="true">⌖</span>현재 위치</button></div><div className="search-row"><label className="search-field"><span aria-hidden="true">⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="시설명 또는 주소 검색" aria-label="시설명 또는 주소 검색" /></label><button className="preview-link" type="button" onClick={() => setPage("simulate")}>재난 상황 미리보기</button></div><div className="category-row" role="group" aria-label="시설 종류">{categoryOrder.map((item) => <button key={item} aria-label={CATEGORY_LABELS[item]} className={category === item ? "category-button selected" : "category-button"} type="button" onClick={() => selectCategory(item)}>{CATEGORY_LABELS[item]}<span>{sourceCounts[item]}</span></button>)}</div><MapView facilities={visibleFacilities} onSelect={setSelected} currentLocation={location} walkingRoute={walkingRoute} /><p className="map-note">{locationMessage || "지도에서 시설을 선택하면 상세 정보를 확인할 수 있습니다."}</p></div><aside className="support-panel" aria-label="주변 재난 대응 안내"><section className="nearby-section"><p className="section-kicker">현재 선택</p><h2>{CATEGORY_LABELS[category]} 찾기</h2>{category === "AED" && <div className="aed-first"><a className="primary-emergency" href="tel:119"><span aria-hidden="true">☎</span><span><strong>119 신고</strong><small>위치 확인보다 신고가 먼저입니다.</small></span></a><button className="secondary-button" type="button" onClick={() => setSelected(visibleFacilities[0] || null)}>AED 찾기</button><p className="notice-text">원문에 좌표가 없어 AED는 주소 목록으로 제공합니다.</p></div>}<div className="nearby-list">{nearby.map((facility) => <button key={facility.id} type="button" onClick={() => setSelected(facility)}><span className="list-dot" aria-hidden="true" /><span><strong>{facility.name || "시설명 미상"}</strong><small>{facility.address || "주소 미상"}</small>{category === "AED" && <small>원문 좌표 없음 · {facility.source_provenance || "OFFICIAL"}</small>}</span></button>)}{nearby.length === 0 && <p className="empty-state">검색 결과가 없습니다. 현재 원문에는 위치정보가 없습니다.</p>}</div></section>{selected && <FacilityDetails facility={selected} onRoute={requestRoute} />}{routeMessage && <p className="route-result" role="status">{routeMessage}</p>}{routeCandidates.length > 1 && <div className="route-candidates" aria-label="다른 도보 경로"><strong>다른 도보 경로</strong>{routeCandidates.slice(1).map((candidate) => <button key={candidate.candidate_index} type="button" onClick={() => chooseRoute(candidate)}>대안 경로 · 약 {candidate.distance_m.toLocaleString()}m · {candidate.estimated_walking_minutes}분</button>)}</div>}<section className="support-note"><h2>실제 재난 시</h2><p>공식 재난문자와 안내를 우선 확인하세요. 이 화면은 보조 정보입니다.</p><a href="tel:119" className="call-link"><span aria-hidden="true">☎</span><span><strong>119 신고</strong><small>긴급 구조·구급</small></span></a></section></aside></main><footer><span>SAFE-Twin 안양 · 현재 연결된 공공데이터 기준</span><button type="button" onClick={() => setPage("about")}>데이터 출처와 한계</button></footer>
  </div>;
}
