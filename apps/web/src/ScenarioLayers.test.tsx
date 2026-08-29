import { describe, expect, it } from "vitest";
import { buildEvacuationFlowGeoJson } from "./MapView";

describe("4D evacuation flow layer", () => {
  it("keeps aggregated demand-to-shelter lines and load ratios", () => {
    const layer = buildEvacuationFlowGeoJson([{ demand_node_id: "d1", shelter_id: "s1", assigned_demand: 42, load_ratio: 0.7, geometry: { type: "LineString", coordinates: [[126.9, 37.4], [126.91, 37.41]] } }]);
    expect(layer.features).toHaveLength(1);
    expect(layer.features[0].properties).toMatchObject({ demand_node_id: "d1", shelter_id: "s1", assigned_demand: 42, load_ratio: 0.7 });
    expect(layer.features[0].geometry.type).toBe("LineString");
  });
});
