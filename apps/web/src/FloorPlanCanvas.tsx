import { useRef, useState } from "react";
import type { EventPoint } from "./eventPlan";

export function FloorPlanCanvas({ width, height, imageUrl, pdfUrl, points, route, onPointAdd }: { width: number; height: number; imageUrl?: string; pdfUrl?: string; points: EventPoint[]; route: EventPoint[]; onPointAdd: (point: EventPoint) => void }) {
  const surface = useRef<SVGSVGElement>(null);
  const drag = useRef<{ x: number; y: number; moved: boolean } | null>(null);
  const suppressClick = useRef(false);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  function addPoint(event: React.MouseEvent<SVGSVGElement>) {
    if (suppressClick.current || drag.current?.moved) { suppressClick.current = false; drag.current = null; return; }
    const rect = surface.current?.getBoundingClientRect();
    const svg = surface.current;
    const matrix = svg && "getScreenCTM" in svg ? svg.getScreenCTM?.() : null;
    if (svg && matrix && "createSVGPoint" in svg) {
      const point = svg.createSVGPoint();
      point.x = event.clientX; point.y = event.clientY;
      const local = point.matrixTransform(matrix.inverse());
      onPointAdd({ x: Math.round(Math.max(0, Math.min(width, local.x))), y: Math.round(Math.max(0, Math.min(height, local.y))) });
      return;
    }
    const scaleX = rect?.width ? width / rect.width : 1;
    const scaleY = rect?.height ? height / rect.height : 1;
    onPointAdd({ x: Math.round(Math.max(0, Math.min(width, ((event.clientX - (rect?.left ?? 0)) - pan.x) / zoom * scaleX))), y: Math.round(Math.max(0, Math.min(height, ((event.clientY - (rect?.top ?? 0)) - pan.y) / zoom * scaleY))) });
  }
  function startPan(event: React.PointerEvent<SVGSVGElement>) { suppressClick.current = false; drag.current = { x: event.clientX, y: event.clientY, moved: false }; }
  function movePan(event: React.PointerEvent<SVGSVGElement>) {
    if (!drag.current) return;
    const dx = event.clientX - drag.current.x;
    const dy = event.clientY - drag.current.y;
    if (Math.abs(dx) + Math.abs(dy) < 2) return;
    drag.current.moved = true;
    drag.current.x = event.clientX; drag.current.y = event.clientY;
    setPan((current) => ({ x: current.x + dx, y: current.y + dy }));
  }
  function endPan() { if (drag.current?.moved) { suppressClick.current = true; drag.current = null; return; } if (drag.current) window.setTimeout(() => { drag.current = null; }, 0); }
  return <section className="floor-plan-editor" aria-label="실내 도면 편집"><div className="floor-plan-tools"><button type="button" onClick={() => setZoom((value) => Math.min(2, value + .1))}>확대</button><button type="button" onClick={() => setZoom((value) => Math.max(.7, value - .1))}>축소</button><span>도면 좌표 {width}×{height} · 드래그하여 이동</span></div><div className="floor-plan-stage">{pdfUrl && <object className="floor-plan-pdf" data={pdfUrl} type="application/pdf" aria-label="업로드한 PDF 도면 첫 페이지"><span>PDF 도면을 표시할 수 없습니다. 원본 파일을 직접 열어 확인하세요.</span></object>}<svg ref={surface} data-testid="floor-plan-surface" role="img" aria-label="실내 도면 위 경로 편집" viewBox={`0 0 ${width} ${height}`} style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`, cursor: drag.current ? "grabbing" : "grab" }} onClick={addPoint} onPointerDown={startPan} onPointerMove={movePan} onPointerUp={endPan} onPointerCancel={endPan}>{imageUrl && <image href={imageUrl} width={width} height={height} preserveAspectRatio="none" />}{!imageUrl && !pdfUrl && <rect width={width} height={height} fill="#eaf5f5" />}{route.length > 1 && <polyline points={route.map((point) => `${point.x},${point.y}`).join(" ")} fill="none" stroke="#b34a3c" strokeWidth="5" />}{points.map((point, index) => <circle key={`${point.x}-${point.y}-${index}`} cx={point.x} cy={point.y} r="8" fill="#0a6472" stroke="#fff" strokeWidth="2" />)}</svg></div></section>;
}
