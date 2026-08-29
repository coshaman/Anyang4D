import { describe, expect, it } from "vitest";
import { addEventNode, addOutdoorNode, addOutdoorRoutePoint, addRoutePoint, buildEventShareUrl, clearEventNode, createEventPlan, decodeEventPlan, encodeEventPlan, removeLastRoutePoint, updateEventGroup, type EventPoint } from "./eventPlan";

describe("event evacuation plan contract", () => {
  it("creates a group plan and preserves image-local points through URL encoding", () => {
    const plan = createEventPlan("안양 해커톤", "안양대학교 강당", "INDOOR");
    const start: EventPoint = { x: 120, y: 80 };
    const withStart = addEventNode(plan, "A", "start", start);
    const withRoute = addRoutePoint(withStart, "A", start);
    const decoded = decodeEventPlan(encodeEventPlan(withRoute));
    expect(decoded.groups[0].start).toEqual(start);
    expect(decoded.groups[0].route).toEqual([start]);
  });

  it("updates one group without changing another group", () => {
    const plan = createEventPlan("행사", "장소", "OUTDOOR");
    const next = updateEventGroup(addEventNode(plan, "B", "exit", { x: 9, y: 8 }), "A", { name: "A구역" });
    expect(next.groups.find((group) => group.id === "B")?.exit).toEqual({ x: 9, y: 8 });
    expect(next.groups.find((group) => group.id === "A")?.name).toBe("A구역");
  });

  it("builds a public event URL with a decodable plan token", () => {
    const plan = createEventPlan("안전 행사", "장소", "OUTDOOR");
    const url = buildEventShareUrl(plan, "https://example.test");
    expect(url).toContain("/event/");
    expect(decodeEventPlan(new URL(url).searchParams.get("plan") ?? "").name).toBe("안전 행사");
  });

  it("removes only the selected group's last manually drawn route point", () => {
    let plan = createEventPlan("행사", "장소", "INDOOR");
    plan = addRoutePoint(addRoutePoint(plan, "A", { x: 1, y: 2 }), "A", { x: 3, y: 4 });
    plan = addRoutePoint(plan, "B", { x: 9, y: 9 });
    const next = removeLastRoutePoint(plan, "A");
    expect(next.groups.find((group) => group.id === "A")?.route).toEqual([{ x: 1, y: 2 }]);
    expect(next.groups.find((group) => group.id === "B")?.route).toEqual([{ x: 9, y: 9 }]);
  });

  it("keeps outdoor map coordinates separate from indoor image coordinates", () => {
    const plan = createEventPlan("야외 행사", "안양 캠퍼스", "OUTDOOR");
    const withStart = addOutdoorNode(plan, "A", "start", { latitude: 37.4, longitude: 126.95 });
    const withExit = addOutdoorNode(withStart, "A", "exit", { latitude: 37.401, longitude: 126.952 });
    const withRoute = addOutdoorRoutePoint(withExit, "A", { latitude: 37.4005, longitude: 126.951 });
    expect(withRoute.groups[0].outdoorStart).toEqual({ latitude: 37.4, longitude: 126.95 });
    expect(withRoute.groups[0].outdoorExit).toEqual({ latitude: 37.401, longitude: 126.952 });
    expect(withRoute.groups[0].outdoorRoute).toEqual([{ latitude: 37.4005, longitude: 126.951 }]);
    expect(withRoute.groups[0].start).toBeNull();
  });

  it("supports a route label and clearing an edited node", () => {
    let plan = createEventPlan("행사", "장소", "INDOOR");
    plan = updateEventGroup(addEventNode(plan, "A", "exit", { x: 10, y: 20 }), "A", { routeLabel: "북쪽 출구 안내" });
    const cleared = clearEventNode(plan, "A", "exit");
    expect(cleared.groups[0].routeLabel).toBe("북쪽 출구 안내");
    expect(cleared.groups[0].exit).toBeNull();
  });
});
