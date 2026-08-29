import { useRef, useState } from "react";
import type { EventPoint } from "./eventPlan";

export function FloorPlanCanvas({ width, height, imageUrl, points, route, onPointAdd }: { width: number; height: number; imageUrl?: string; points: EventPoint[]; route: EventPoint[]; onPointAdd: (point: EventPoint) => void }) {
  const surface = useRef<SVGSVGElement>(null);
  const drag = useRef<{ x: number; y: number; moved: boolean } | null>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  function addPoint(event: React.MouseEvent<SVGSVGElement>) {
    if (drag.current?.moved) { drag.current = null; return; }
    const rect = surface.current?.getBoundingClientRect();
    const scaleX = rect?.width ? width / rect.width : 1;
    const scaleY = rect?.height ? height / rect.height : 1;
    onPointAdd({ x: Math.round((event.clientX - (rect?.left ?? 0)) * scaleX), y: Math.round((event.clientY - (rect?.top ?? 0)) * scaleY) });
  }
  function startPan(event: React.PointerEvent<SVGSVGElement>) { drag.current = { x: event.clientX, y: event.clientY, moved: false }; }
  function movePan(event: React.PointerEvent<SVGSVGElement>) {
    if (!drag.current) return;
    const dx = event.clientX - drag.current.x;
    const dy = event.clientY - drag.current.y;
    if (Math.abs(dx) + Math.abs(dy) < 2) return;
    drag.current.moved = true;
    drag.current.x = event.clientX; drag.current.y = event.clientY;
    setPan((current) => ({ x: current.x + dx, y: current.y + dy }));
  }
  function endPan() { if (drag.current && !drag.current.moved) window.setTimeout(() => { drag.current = null; }, 0); }
  return <section className="floor-plan-editor" aria-label="실내 도면 편집"><div className="floor-plan-tools"><button type="button" onClick={() => setZoom((value) => Math.min(2, value + .1))}>확대</button><button type="button" onClick={() => setZoom((value) => Math.max(.7, value - .1))}>축소</button><span>도면 좌표 {width}×{height} · 드래그하여 이동</span></div><svg ref={surface} data-testid="floor-plan-surface" role="img" aria-label="실내 도면 위 경로 편집" viewBox={`0 0 ${width} ${height}`} style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`, cursor: drag.current ? "grabbing" : "grab" }} onClick={addPoint} onPointerDown={startPan} onPointerMove={movePan} onPointerUp={endPan} onPointerCancel={endPan}>{imageUrl && <image href={imageUrl} width={width} height={height} preserveAspectRatio="none" />}{!imageUrl && <rect width={width} height={height} fill="#eaf5f5" />}{route.length > 1 && <polyline points={route.map((point) => `${point.x},${point.y}`).join(" ")} fill="none" stroke="#b34a3c" strokeWidth="5" />}{points.map((point, index) => <circle key={`${point.x}-${point.y}-${index}`} cx={point.x} cy={point.y} r="8" fill="#0a6472" stroke="#fff" strokeWidth="2" />)}</svg></section>;
}
