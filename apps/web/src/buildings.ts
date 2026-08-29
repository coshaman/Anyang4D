export type OSMBuilding = {
  id: string;
  geometry: { type: "Polygon"; coordinates: number[][][] };
  tags: Record<string, string>;
};

// OSM snapshot 2026-08-20: incomplete building coverage, used only as a visual map layer.
export const osmBuildings: OSMBuilding[] = [{
  id: "osm-way-559348960",
  geometry: { type: "Polygon", coordinates: [[
    [126.9936764, 37.4296288], [126.9936926, 37.4296049], [126.9937292, 37.4295824],
    [126.9937746, 37.4295637], [126.9938143, 37.4295625], [126.9938159, 37.4295953],
    [126.9938054, 37.4296284], [126.9937773, 37.4296494], [126.9937434, 37.4296592],
    [126.9937033, 37.4296518], [126.9936764, 37.4296288]
  ]] },
  tags: { building: "yes", amenity: "theatre", name: "OSM building footprint" }
}];
