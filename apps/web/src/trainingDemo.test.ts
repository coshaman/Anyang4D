import { describe, expect, it } from "vitest";
import { trainingDemoFrames, trainingDemoScenario } from "./trainingDemo";

describe("public precomputed training demo", () => {
  it("contains four distinct overlay states", () => {
    expect(trainingDemoScenario.frame_times).toEqual([0, 10, 20, 30]);
    const states = trainingDemoScenario.frame_times.map((minute) => trainingDemoFrames[minute]);
    expect(states).toHaveLength(4);
    expect(states.map((frame) => frame.roads.changed_count)).toEqual([0, 2, 3, 4]);
    expect(states.map((frame) => frame.available_shelter_count)).toEqual([18, 17, 16, 15]);
    expect(states.map((frame) => frame.assignment.unserved)).toEqual([1324, 1564, 2434, 3924]);
  });
});
