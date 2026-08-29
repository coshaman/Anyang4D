import type { EventPlan, EventPoint, OutdoorPoint } from "./eventPlan";

export type StoryboardScene = { id: string; title: string; caption: string; points: EventPoint[]; durationSeconds: number };

export function buildStoryboard(plan: EventPlan, groupId = "A"): StoryboardScene[] {
  const group = plan.groups.find((item) => item.id === groupId) ?? plan.groups[0];
  const outdoorPoints = [group?.outdoorStart, ...(group?.outdoorRoute ?? []), group?.outdoorExit, group?.outdoorAssembly].filter((point): point is OutdoorPoint => Boolean(point));
  const projectedOutdoor = projectOutdoorPoints(outdoorPoints);
  const hasOutdoorStart = Boolean(group?.outdoorStart);
  const hasOutdoorExit = Boolean(group?.outdoorExit);
  const outdoorStart = hasOutdoorStart ? projectedOutdoor.slice(0, 1) : [];
  const outdoorRoute = group?.outdoorRoute?.length ? projectedOutdoor.slice(hasOutdoorStart ? 1 : 0, (hasOutdoorStart ? 1 : 0) + group.outdoorRoute.length) : [];
  const outdoorExit = hasOutdoorExit ? projectedOutdoor.slice((hasOutdoorStart ? 1 : 0) + (group?.outdoorRoute?.length ?? 0), (hasOutdoorStart ? 1 : 0) + (group?.outdoorRoute?.length ?? 0) + 1) : [];
  const outdoorAssembly = group?.outdoorAssembly ? projectedOutdoor.slice(-1) : [];
  const start = group?.start ? [group.start] : outdoorStart;
  const exit = group?.exit ? [group.exit] : outdoorExit;
  const assembly = group?.assembly ? [group.assembly] : outdoorAssembly;
  const route = group?.route?.length ? group.route : outdoorRoute.length ? outdoorRoute : projectedOutdoor;
  const duration = Math.max(2, Math.min(15, plan.videoConfig?.sceneDurationSeconds ?? 3));
  return [
    { id: "title", title: plan.videoConfig?.title || plan.name || "행사", caption: "비상 대피 안내", points: [], durationSeconds: duration },
    { id: "start", title: "현재 참가자 구역", caption: `${group?.name ?? "A구역"}에서 안내를 시작합니다.`, points: start, durationSeconds: duration },
    { id: "exit", title: "지정 비상 출구", caption: "운영자가 지정한 출구로 이동하세요.", points: exit, durationSeconds: duration },
    { id: "route-exit", title: "출구까지 이동", caption: "뛰지 말고 안내 경로를 따라가세요.", points: route, durationSeconds: duration },
    { id: "route-assembly", title: "집결지까지 이동", caption: "출구를 지나 지정 집결지로 이동하세요.", points: [...route, ...assembly], durationSeconds: duration },
    { id: "instructions", title: "비상 행동", caption: plan.emergencyInstructions.join(" · "), points: [], durationSeconds: duration },
  ];
}

function projectOutdoorPoints(points: OutdoorPoint[]): EventPoint[] {
  if (!points.length) return [];
  const longitudes = points.map((point) => point.longitude);
  const latitudes = points.map((point) => point.latitude);
  const minLon = Math.min(...longitudes), maxLon = Math.max(...longitudes), minLat = Math.min(...latitudes), maxLat = Math.max(...latitudes);
  const lonRange = Math.max(0.00001, maxLon - minLon), latRange = Math.max(0.00001, maxLat - minLat);
  return points.map((point) => ({ x: 120 + ((point.longitude - minLon) / lonRange) * 680, y: 120 + ((maxLat - point.latitude) / latRange) * 520 }));
}

export function sceneAtTime(storyboard: StoryboardScene[], elapsedSeconds: number) {
  let cursor = 0;
  for (let index = 0; index < storyboard.length; index += 1) {
    cursor += storyboard[index].durationSeconds;
    if (elapsedSeconds < cursor) return index;
  }
  return Math.max(0, storyboard.length - 1);
}

export function canExportWebm(hasMediaRecorder: boolean, hasCaptureStream: boolean) {
  return hasMediaRecorder && hasCaptureStream;
}

export function sceneProgress(storyboard: StoryboardScene[], elapsedSeconds: number) {
  let cursor = 0;
  for (let index = 0; index < storyboard.length; index += 1) {
    const duration = storyboard[index].durationSeconds;
    if (elapsedSeconds < cursor + duration) return { index, progress: Math.max(0, Math.min(1, (elapsedSeconds - cursor) / duration)) };
    cursor += duration;
  }
  return { index: Math.max(0, storyboard.length - 1), progress: 1 };
}
