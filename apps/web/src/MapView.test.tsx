import { describe, expect, it } from "vitest";
import { buildBuildingGeoJson, buildBuildingExtrusionLayer, eventSafetyPointGeoJson, normalizeBuilding } from "./MapView";

describe("2.5D building map contract", () => {
  it("prefers OSM height, then derives levels, then marks unknown height", () => {
    expect(normalizeBuilding({ id: "osm-1", geometry: { type: "Polygon", coordinates: [] }, tags: { height: "12.5", "building:levels": "4" } })).toMatchObject({ height_m: 12.5, height_provenance: "OSM_HEIGHT" });
    expect(normalizeBuilding({ id: "osm-2", geometry: { type: "Polygon", coordinates: [] }, tags: { "building:levels": "4" } })).toMatchObject({ height_m: 12, height_provenance: "DERIVED_LEVEL_HEIGHT" });
    expect(normalizeBuilding({ id: "osm-3", geometry: { type: "Polygon", coordinates: [] }, tags: {} })).toMatchObject({ height_m: 0, height_provenance: "UNKNOWN_HEIGHT" });
  });

  it("publishes an extrusion layer with provenance in building source properties", () => {
    const feature = normalizeBuilding({ id: "osm-2", geometry: { type: "Polygon", coordinates: [[[126.9, 37.4]]] }, tags: { "building:levels": "3" } });
    const collection = buildBuildingGeoJson([feature]);
    expect(collection.features[0].properties).toMatchObject({ height_m: 9, height_provenance: "DERIVED_LEVEL_HEIGHT" });
    expect(buildBuildingExtrusionLayer()).toMatchObject({ id: "building-extrusion", type: "fill-extrusion", source: "buildings" });
  });

  it("publishes outdoor event safety points as labeled map features", () => {
    const layer = eventSafetyPointGeoJson([{ kind: "AED", point: { latitude: 37.4, longitude: 126.95 } }, { kind: "RESTRICTED_ZONE", point: { latitude: 37.401, longitude: 126.951 }, label: "공사 구역" }]);
    expect(layer.features).toHaveLength(2);
    expect(layer.features[0].geometry.coordinates).toEqual([126.95, 37.4]);
    expect(layer.features[0].properties.label).toBe("AED");
    expect(layer.features[1].properties.label).toBe("공사 구역");
  });
});
