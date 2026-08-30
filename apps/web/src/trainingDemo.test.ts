import { describe, expect, it } from "vitest";
import { describeTrainingFrame, trainingDemoFrames, trainingDemoScenario } from "./trainingDemo";

describe("public precomputed training demo", () => {
  it("contains four distinct overlay states", () => {
    expect(trainingDemoScenario.frame_times).toEqual([0, 10, 20, 30]);
    const states = trainingDemoScenario.frame_times.map((minute) => trainingDemoFrames[minute]);
    expect(states).toHaveLength(4);
    expect(states.map((frame) => frame.roads.changed_count)).toEqual([0, 2, 3, 4]);
    expect(states.map((frame) => frame.available_shelter_count)).toEqual([18, 17, 16, 15]);
    expect(states.map((frame) => frame.assignment.unserved)).toEqual([1324, 1564, 2434, 3924]);
  });

  it("changes the spatial hazard extent at every training step", () => {
    const hazards = trainingDemoScenario.frame_times.map((minute) => JSON.stringify(trainingDemoFrames[minute].hazard.geometry));
    expect(new Set(hazards).size).toBe(trainingDemoScenario.frame_times.length);
  });

  it("explains the operational meaning of the current frame", () => {
    expect(describeTrainingFrame(trainingDemoFrames[20], 20)).toContain("통행 제한");
    expect(describeTrainingFrame(trainingDemoFrames[30], 30)).toContain("가용 대피소");
  });
});
