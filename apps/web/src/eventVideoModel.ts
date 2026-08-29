import type { EventPlan, EventPoint } from "./eventPlan";

export type StoryboardScene = { id: string; title: string; caption: string; points: EventPoint[]; durationSeconds: number };

export function buildStoryboard(plan: EventPlan, groupId = "A"): StoryboardScene[] {
  const group = plan.groups.find((item) => item.id === groupId) ?? plan.groups[0];
  const start = group?.start ? [group.start] : [];
  const exit = group?.exit ? [group.exit] : [];
  const assembly = group?.assembly ? [group.assembly] : [];
  return [
    { id: "title", title: plan.name || "행사", caption: "비상 대피 안내", points: [], durationSeconds: 3 },
    { id: "start", title: "현재 참가자 구역", caption: `${group?.name ?? "A구역"}에서 안내를 시작합니다.`, points: start, durationSeconds: 3 },
    { id: "exit", title: "지정 비상 출구", caption: "운영자가 지정한 출구로 이동하세요.", points: exit, durationSeconds: 3 },
    { id: "route-exit", title: "출구까지 이동", caption: "뛰지 말고 안내 경로를 따라가세요.", points: group?.route ?? [], durationSeconds: 4 },
    { id: "route-assembly", title: "집결지까지 이동", caption: "출구를 지나 지정 집결지로 이동하세요.", points: [...(group?.route ?? []), ...assembly], durationSeconds: 4 },
    { id: "instructions", title: "비상 행동", caption: plan.emergencyInstructions.join(" · "), points: [], durationSeconds: 4 },
  ];
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
