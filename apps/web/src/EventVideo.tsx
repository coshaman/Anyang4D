import { useEffect, useMemo, useRef, useState } from "react";
import type { EventPlan, EventPoint } from "./eventPlan";
import { buildStoryboard, canExportWebm, sceneAtTime, sceneProgress } from "./eventVideoModel";

export function EventVideo({ plan, groupId = "A" }: { plan: EventPlan; groupId?: string }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const storyboard = useMemo(() => buildStoryboard(plan, groupId), [plan, groupId]);
  const [elapsed, setElapsed] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [exportStatus, setExportStatus] = useState("");
  const sceneIndex = sceneAtTime(storyboard, elapsed);
  const scene = storyboard[sceneIndex];
  const progress = sceneProgress(storyboard, elapsed).progress;

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => setElapsed((value) => value + 0.1), 100);
    return () => window.clearInterval(timer);
  }, [playing]);

  useEffect(() => {
    const context = canvas.current?.getContext("2d");
    if (!context || !scene) return;
    context.clearRect(0, 0, 1920, 1080);
    context.fillStyle = "#edf5f4"; context.fillRect(0, 0, 1920, 1080);
    context.fillStyle = "#0a6472"; context.fillRect(0, 0, 1920, 150);
    context.fillStyle = "#ffffff"; context.font = "500 54px sans-serif"; context.fillText(scene.title, 100, 95);
    context.fillStyle = "#173d43"; context.font = "500 42px sans-serif"; context.fillText(scene.caption, 100, 240);
    const animatedPoints = scene.id.startsWith("route-") ? scene.points.slice(0, Math.max(1, Math.ceil(scene.points.length * progress))) : scene.points;
    if (animatedPoints.length > 0) {
      context.strokeStyle = "#b34a3c"; context.lineWidth = 16; context.lineJoin = "round"; context.beginPath();
      animatedPoints.forEach((point, index) => { const x = 180 + point.x * 1.6; const y = 360 + point.y * 1.2; if (index === 0) context.moveTo(x, y); else context.lineTo(x, y); });
      context.stroke();
      animatedPoints.forEach((point, index) => { context.fillStyle = index === 0 ? "#0a6472" : "#b34a3c"; context.beginPath(); context.arc(180 + point.x * 1.6, 360 + point.y * 1.2, 26, 0, Math.PI * 2); context.fill(); });
    }
    context.fillStyle = "#53636a"; context.font = "400 30px sans-serif"; context.fillText(`비상 대피 안내 · ${sceneIndex + 1}/6`, 100, 1000);
  }, [scene, sceneIndex, progress]);

  async function exportWebm() {
    const target = canvas.current;
    if (!target || !canExportWebm(typeof MediaRecorder !== "undefined", Boolean(target.captureStream))) { setExportStatus("이 브라우저는 WebM 내보내기를 지원하지 않습니다."); return; }
    try {
    const stream = target.captureStream(30);
    const chunks: BlobPart[] = [];
    const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });
    recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data); };
    recorder.onstop = () => { const url = URL.createObjectURL(new Blob(chunks, { type: "video/webm" })); const link = document.createElement("a"); link.href = url; link.download = `${plan.slug || "event"}-evacuation-guide.webm`; link.click(); URL.revokeObjectURL(url); };
    recorder.start(); setPlaying(true); window.setTimeout(() => { setPlaying(false); recorder.stop(); }, 1600);
    setExportStatus("WebM을 준비하고 있습니다.");
    } catch { setExportStatus("WebM 내보내기를 시작하지 못했습니다."); }
  }

  return <section className="event-video" aria-label="대피 안내 영상 미리보기"><h2>비상 대피 안내 영상</h2><canvas ref={canvas} width={1920} height={1080} data-testid="event-video-canvas" data-scene-index={sceneIndex} role="img" aria-label={`${sceneIndex + 1}번째 영상 장면 · ${scene.title}`} /><p className="event-video-caption">행사 운영자가 지정한 경로를 안내자료로 보여줍니다. 법정 안전 인증 영상이 아닙니다.</p><div className="video-controls"><button type="button" onClick={() => setPlaying((value) => !value)}>{playing ? "일시정지" : "재생"}</button><button type="button" onClick={() => { setElapsed(0); setPlaying(false); }}>처음부터</button><button type="button" onClick={() => void exportWebm()}>WebM 내보내기</button><button type="button" onClick={() => void canvas.current?.requestFullscreen?.()}>전체 화면</button><span>장면 {sceneIndex + 1}/6</span></div>{exportStatus && <p role="status">{exportStatus}</p>}</section>;
}
