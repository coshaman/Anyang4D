import { useEffect, useMemo, useRef, useState } from "react";
import type { EventPlan, EventPoint } from "./eventPlan";
import { buildStoryboard, canExportWebm, sceneAtTime, sceneProgress } from "./eventVideoModel";

export function EventVideo({ plan, groupId = "A" }: { plan: EventPlan; groupId?: string }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const backgroundImage = useRef<HTMLImageElement | null>(null);
  const storyboard = useMemo(() => buildStoryboard(plan, groupId), [plan, groupId]);
  const [elapsed, setElapsed] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [exportStatus, setExportStatus] = useState("");
  const [backgroundReady, setBackgroundReady] = useState(0);
  const sceneIndex = sceneAtTime(storyboard, elapsed);
  const scene = storyboard[sceneIndex];
  const progress = sceneProgress(storyboard, elapsed).progress;

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => setElapsed((value) => value + 0.1), 100);
    return () => window.clearInterval(timer);
  }, [playing]);

  useEffect(() => {
    const synthesis = typeof window !== "undefined" ? window.speechSynthesis : undefined;
    if (!playing || plan.videoConfig?.narration !== "tts-preview" || !synthesis || !scene) return;
    synthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(`${scene.title}. ${scene.caption}`);
    utterance.lang = "ko-KR";
    synthesis.speak(utterance);
    return () => synthesis.cancel();
  }, [playing, plan.videoConfig?.narration, scene]);

  useEffect(() => {
    backgroundImage.current = null;
    const dataUrl = plan.representation === "INDOOR" && plan.floorPlan?.mimeType !== "application/pdf" ? plan.floorPlan?.dataUrl : undefined;
    if (!dataUrl) { setBackgroundReady((value) => value + 1); return; }
    const image = new Image();
    image.onload = () => { backgroundImage.current = image; setBackgroundReady((value) => value + 1); };
    image.src = dataUrl;
    return () => { image.onload = null; };
  }, [plan.representation, plan.floorPlan?.dataUrl, plan.floorPlan?.mimeType]);

  useEffect(() => {
    const context = canvas.current?.getContext("2d");
    if (!context || !scene) return;
    const draw = (background?: HTMLImageElement) => {
      context.clearRect(0, 0, 1920, 1080);
      context.fillStyle = "#edf5f4"; context.fillRect(0, 0, 1920, 1080);
      if (background) drawImageCover(context, background, 80, 190, 1760, 760);
      else if (plan.representation === "OUTDOOR") drawOutdoorMapBackground(context);
      else drawIndoorPlaceholder(context);
      context.fillStyle = "rgba(10, 100, 114, .96)"; context.fillRect(0, 0, 1920, 150);
      const textScale = plan.videoConfig?.textSize === "large" ? 1.25 : plan.videoConfig?.textSize === "compact" ? .82 : 1;
      context.fillStyle = "#ffffff"; context.font = `500 ${Math.round(54 * textScale)}px sans-serif`; context.fillText(scene.title, 100, 95);
      context.fillStyle = "#173d43"; context.font = `500 ${Math.round(42 * textScale)}px sans-serif`; context.fillText(scene.caption, 100, 240);
      const animatedPoints = scene.id.startsWith("route-") ? scene.points.slice(0, Math.max(1, Math.ceil(scene.points.length * progress))) : scene.points;
      if (animatedPoints.length > 0) {
        context.strokeStyle = "#b34a3c"; context.lineWidth = 16; context.lineJoin = "round"; context.beginPath();
        animatedPoints.forEach((point, index) => { const x = 180 + point.x * 1.6; const y = 360 + point.y * 1.2; if (index === 0) context.moveTo(x, y); else context.lineTo(x, y); });
        context.stroke();
        animatedPoints.forEach((point, index) => { context.fillStyle = index === 0 ? "#0a6472" : "#b34a3c"; context.beginPath(); context.arc(180 + point.x * 1.6, 360 + point.y * 1.2, 26, 0, Math.PI * 2); context.fill(); });
      }
      if (plan.videoConfig?.logoDataUrl) { const logo = new Image(); logo.onload = () => context.drawImage(logo, 1700, 35, 140, 80); logo.src = plan.videoConfig.logoDataUrl; }
      context.fillStyle = "#53636a"; context.font = "400 30px sans-serif"; context.fillText(`비상 대피 안내 · ${sceneIndex + 1}/6`, 100, 1000);
    };
    draw(backgroundImage.current ?? undefined);
  }, [plan, scene, sceneIndex, progress, backgroundReady]);

  async function exportWebm() {
    const target = canvas.current;
    if (!target || !canExportWebm(typeof MediaRecorder !== "undefined", Boolean(target.captureStream))) { setExportStatus("이 브라우저는 WebM 내보내기를 지원하지 않습니다."); return; }
    try {
    const stream = target.captureStream(30);
    const chunks: BlobPart[] = [];
    const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });
    recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data); };
    recorder.onstop = () => { stream.getTracks().forEach((track) => track.stop()); const url = URL.createObjectURL(new Blob(chunks, { type: "video/webm" })); const link = document.createElement("a"); link.href = url; link.download = `${plan.slug || "event"}-evacuation-guide.webm`; link.click(); URL.revokeObjectURL(url); };
    recorder.start();
    setPlaying(false);
    const totalSeconds = storyboard.reduce((sum, item) => sum + item.durationSeconds, 0);
    const captureWindowMs = 2400;
    const exportStarted = performance.now();
    const nextFrame = () => new Promise<void>((resolve) => window.requestAnimationFrame(() => resolve()));
    while (performance.now() - exportStarted < captureWindowMs) {
      setElapsed(Math.min(totalSeconds, ((performance.now() - exportStarted) / captureWindowMs) * totalSeconds));
      await nextFrame();
    }
    setElapsed(totalSeconds);
    await nextFrame();
    recorder.stop();
    setExportStatus("WebM을 준비하고 있습니다.");
    } catch { setExportStatus("WebM 내보내기를 시작하지 못했습니다."); }
  }

  return <section className="event-video" aria-label="대피 안내 영상 미리보기"><h2>비상 대피 안내 영상</h2><canvas ref={canvas} width={1920} height={1080} data-testid="event-video-canvas" data-scene-index={sceneIndex} role="img" aria-label={`${sceneIndex + 1}번째 영상 장면 · ${scene.title}`} /><p className="event-video-caption">행사 운영자가 지정한 경로를 안내자료로 보여줍니다.</p><div className="video-controls"><button type="button" onClick={() => setPlaying((value) => !value)}>{playing ? "일시정지" : "재생"}</button><button type="button" onClick={() => { setElapsed(0); setPlaying(false); }}>처음부터</button><button type="button" onClick={() => void exportWebm()}>WebM 내보내기</button><button type="button" onClick={() => void canvas.current?.requestFullscreen?.()}>전체 화면</button><span>장면 {sceneIndex + 1}/6</span></div>{exportStatus && <p role="status">{exportStatus}</p>}</section>;
}

function drawImageCover(context: CanvasRenderingContext2D, image: HTMLImageElement, x: number, y: number, width: number, height: number) {
  const scale = Math.max(width / image.naturalWidth, height / image.naturalHeight);
  const drawWidth = image.naturalWidth * scale, drawHeight = image.naturalHeight * scale;
  context.save(); context.globalAlpha = 0.82; context.beginPath(); context.rect(x, y, width, height); context.clip();
  context.drawImage(image, x + (width - drawWidth) / 2, y + (height - drawHeight) / 2, drawWidth, drawHeight); context.restore();
}

function drawOutdoorMapBackground(context: CanvasRenderingContext2D) {
  context.fillStyle = "#dbe9e6"; context.fillRect(80, 190, 1760, 760);
  context.strokeStyle = "rgba(255,255,255,.9)"; context.lineWidth = 12;
  for (let x = 80; x <= 1840; x += 220) { context.beginPath(); context.moveTo(x, 190); context.lineTo(x + 180, 950); context.stroke(); }
  for (let y = 250; y <= 900; y += 180) { context.beginPath(); context.moveTo(80, y); context.lineTo(1840, y - 70); context.stroke(); }
  context.fillStyle = "rgba(103,155,154,.42)";
  for (const [x, y, width, height] of [[180, 290, 190, 100], [610, 510, 250, 120], [1120, 300, 220, 130], [1450, 650, 240, 110]] as const) context.fillRect(x, y, width, height);
}

function drawIndoorPlaceholder(context: CanvasRenderingContext2D) {
  context.fillStyle = "#f6f1e8"; context.fillRect(80, 190, 1760, 760);
  context.strokeStyle = "#c8bda8"; context.lineWidth = 5; context.strokeRect(120, 230, 1680, 680);
  context.strokeStyle = "#d9cfbd"; context.lineWidth = 3;
  for (const x of [420, 760, 1100, 1440]) { context.beginPath(); context.moveTo(x, 230); context.lineTo(x, 910); context.stroke(); }
  for (const y of [450, 680]) { context.beginPath(); context.moveTo(120, y); context.lineTo(1800, y); context.stroke(); }
  context.fillStyle = "#8c806b"; context.font = "500 28px sans-serif"; context.fillText("실내 도면을 업로드하면 영상 배경으로 사용됩니다", 170, 285);
}
