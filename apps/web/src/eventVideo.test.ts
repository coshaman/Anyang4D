import { describe, expect, it } from "vitest";
import { buildStoryboard, sceneAtTime } from "./eventVideoModel";
import { createEventPlan, addEventNode, addRoutePoint } from "./eventPlan";

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
});
