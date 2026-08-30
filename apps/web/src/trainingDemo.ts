export type TrainingDemoScenario = {
  scenario_id: string;
  title: string;
  frame_times: number[];
};

export type TrainingDemoFrame = {
  hazard: { geometry: Record<string, unknown>; label: string; provenance: string };
  roads: { changed_count: number; changed: Array<{ a: [number, number]; b: [number, number]; reason: string }> };
  facilities: Array<{ facility_id: string; load: number; available: boolean }>;
  available_shelter_count: number;
  assignment: { evacuation_demand: number; assigned: number; unserved: number; average_assigned_travel_distance_m: number };
  evacuation_flow: Array<{ demand_node_id: string; shelter_id: string; assigned_demand: number; load_ratio: number; geometry: { type: "LineString"; coordinates: number[][] } }>;
  terrain_authorized: boolean;
  citizen_guidance_authorized: boolean;
  computation_status: string;
};

export const trainingDemoScenario: TrainingDemoScenario = {
  scenario_id: "anyang-civil-defense-outage",
  title: "안양 일반 대피 훈련",
  frame_times: [0, 10, 20, 30],
};

const hazard = { type: "Polygon", coordinates: [[[126.93, 37.38], [126.96, 37.38], [126.96, 37.41], [126.93, 37.41], [126.93, 37.38]]] };

export const trainingDemoFrames: Record<number, TrainingDemoFrame> = {
  0: { hazard: { geometry: hazard, label: "훈련용 영향 영역", provenance: "ADMIN_SCENARIO" }, roads: { changed_count: 0, changed: [] }, facilities: [{ facility_id: "demo-shelter-1", load: 0.42, available: true }], available_shelter_count: 18, assignment: { evacuation_demand: 18944, assigned: 17620, unserved: 1324, average_assigned_travel_distance_m: 680 }, evacuation_flow: [{ demand_node_id: "anyang-dong-01", shelter_id: "demo-shelter-1", assigned_demand: 17620, load_ratio: 0.42, geometry: { type: "LineString", coordinates: [[126.91, 37.395], [126.95, 37.395]] } }], terrain_authorized: false, citizen_guidance_authorized: false, computation_status: "DEMO_PRECOMPUTED" },
  10: { hazard: { geometry: hazard, label: "훈련용 영향 영역", provenance: "ADMIN_SCENARIO" }, roads: { changed_count: 2, changed: [{ a: [126.925, 37.39], b: [126.945, 37.39], reason: "훈련용 통행 제한" }, { a: [126.95, 37.4], b: [126.97, 37.4], reason: "훈련용 통행 제한" }] }, facilities: [{ facility_id: "demo-shelter-1", load: 0.61, available: true }], available_shelter_count: 17, assignment: { evacuation_demand: 18944, assigned: 17380, unserved: 1564, average_assigned_travel_distance_m: 760 }, evacuation_flow: [{ demand_node_id: "anyang-dong-01", shelter_id: "demo-shelter-1", assigned_demand: 17380, load_ratio: 0.61, geometry: { type: "LineString", coordinates: [[126.91, 37.395], [126.94, 37.395], [126.95, 37.4]] } }], terrain_authorized: false, citizen_guidance_authorized: false, computation_status: "DEMO_PRECOMPUTED" },
  20: { hazard: { geometry: hazard, label: "훈련용 영향 영역", provenance: "ADMIN_SCENARIO" }, roads: { changed_count: 3, changed: [{ a: [126.925, 37.39], b: [126.945, 37.39], reason: "훈련용 통행 제한" }, { a: [126.95, 37.4], b: [126.97, 37.4], reason: "훈련용 통행 제한" }, { a: [126.93, 37.405], b: [126.95, 37.405], reason: "훈련용 통행 제한" }] }, facilities: [{ facility_id: "demo-shelter-1", load: 0.84, available: true }], available_shelter_count: 16, assignment: { evacuation_demand: 18944, assigned: 16510, unserved: 2434, average_assigned_travel_distance_m: 910 }, evacuation_flow: [{ demand_node_id: "anyang-dong-01", shelter_id: "demo-shelter-1", assigned_demand: 16510, load_ratio: 0.84, geometry: { type: "LineString", coordinates: [[126.91, 37.395], [126.93, 37.395], [126.95, 37.4]] } }], terrain_authorized: false, citizen_guidance_authorized: false, computation_status: "DEMO_PRECOMPUTED" },
  30: { hazard: { geometry: hazard, label: "훈련용 영향 영역", provenance: "ADMIN_SCENARIO" }, roads: { changed_count: 4, changed: [{ a: [126.925, 37.39], b: [126.945, 37.39], reason: "훈련용 통행 제한" }, { a: [126.95, 37.4], b: [126.97, 37.4], reason: "훈련용 통행 제한" }, { a: [126.93, 37.405], b: [126.95, 37.405], reason: "훈련용 통행 제한" }, { a: [126.94, 37.385], b: [126.94, 37.415], reason: "훈련용 통행 제한" }] }, facilities: [{ facility_id: "demo-shelter-1", load: 0, available: false }], available_shelter_count: 15, assignment: { evacuation_demand: 18944, assigned: 15020, unserved: 3924, average_assigned_travel_distance_m: 1100 }, evacuation_flow: [{ demand_node_id: "anyang-dong-01", shelter_id: "demo-shelter-1", assigned_demand: 15020, load_ratio: 0, geometry: { type: "LineString", coordinates: [[126.91, 37.395], [126.92, 37.4], [126.95, 37.4]] } }], terrain_authorized: false, citizen_guidance_authorized: false, computation_status: "DEMO_PRECOMPUTED" },
};
