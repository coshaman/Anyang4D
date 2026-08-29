import { describe, expect, it } from "vitest";
import { addEventNode, addRoutePoint, buildEventShareUrl, createEventPlan, decodeEventPlan, encodeEventPlan, updateEventGroup, type EventPoint } from "./eventPlan";

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
});
