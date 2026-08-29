import { describe, expect, it } from "vitest";
import { buildStoryboard, canExportWebm, sceneAtTime, sceneProgress } from "./eventVideoModel";
import { addEventNode, addOutdoorNode, addOutdoorRoutePoint, addRoutePoint, createEventPlan } from "./eventPlan";

describe("deterministic evacuation video storyboard", () => {
  it("contains six scenes and carries the group route into route scenes", () => {
    let plan = createEventPlan("행사", "강당", "INDOOR");
    plan = addEventNode(plan, "A", "start", { x: 20, y: 20 });
    plan = addEventNode(plan, "A", "exit", { x: 180, y: 160 });
    plan = addEventNode(plan, "A", "assembly", { x: 260, y: 200 });
    plan = addRoutePoint(addRoutePoint(plan, "A", { x: 20, y: 20 }), "A", { x: 180, y: 160 });
    const storyboard = buildStoryboard(plan, "A");
    expect(storyboard).toHaveLength(6);
    expect(storyboard[3].points).toEqual(plan.groups[0].route);
    expect(sceneAtTime(storyboard, 0.99)).toBe(0);
    expect(sceneAtTime(storyboard, 3.01)).toBe(1);
  });

  it("reports whether the browser can export WebM", () => {
    expect(canExportWebm(false, false)).toBe(false);
    expect(canExportWebm(true, true)).toBe(true);
  });

  it("progresses route scenes over time instead of drawing them all at once", () => {
    const storyboard = buildStoryboard(createEventPlan("행사", "장소", "INDOOR"), "A");
    expect(sceneProgress(storyboard, 9.1).progress).toBeGreaterThan(0);
    expect(sceneProgress(storyboard, 9.1).progress).toBeLessThan(1);
    expect(sceneProgress(storyboard, 13).index).toBe(4);
  });

  it("projects an outdoor route into one shared video coordinate system", () => {
    let plan = createEventPlan("야외 행사", "캠퍼스", "OUTDOOR");
    plan = addOutdoorNode(plan, "A", "start", { latitude: 37.4, longitude: 126.95 });
    plan = addOutdoorNode(plan, "A", "exit", { latitude: 37.402, longitude: 126.954 });
    plan = addOutdoorRoutePoint(plan, "A", { latitude: 37.401, longitude: 126.952 });
    const route = buildStoryboard(plan)[3].points;
    expect(route).toHaveLength(1);
    expect(route[0].x).toBeGreaterThan(120);
    expect(route[0].y).toBeGreaterThan(120);
  });
});
