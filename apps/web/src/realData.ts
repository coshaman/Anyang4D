import processed from "../../../data/processed/anyang_facilities.json";
import manifest from "../../../data/manifests/data_manifest.json";

export type Category = "CIVIL_DEFENSE_SHELTER" | "EMERGENCY_WATER" | "AED";

export type Facility = {
  id: string;
  source_dataset_id: string;
  name: string | null;
  category: Category;
  latitude: number | null;
  longitude: number | null;
  source_crs: string | null;
  address: string | null;
  provider: string;
  source_update_timestamp: string | null;
  retrieval_timestamp: string | null;
  provenance: "OFFICIAL";
  source_provenance?: "NATIONAL_OFFICIAL_FILTERED_ANYANG" | "ANYANG_LOCAL_OFFICIAL";
  raw_source_reference: string | null;
  capacity: number | null;
  operating_info: string | null;
  access_info: string | null;
  disaster_suitability: string | null;
  data_quality_flags: string[];
  facility_position?: string | null;
  area_m2?: number | null;
};

export const facilities = processed.records as Facility[];

export const CATEGORY_LABELS: Record<Category, string> = {
  CIVIL_DEFENSE_SHELTER: "대피소",
  EMERGENCY_WATER: "급수시설",
  AED: "AED"
};

export const RETRIEVAL_TIMESTAMP = "2026-08-20T11:33:08+00:00";
export const dataManifest = manifest.datasets;

export const sourceCounts = facilities.reduce<Record<Category, number>>((counts, facility) => {
  counts[facility.category] += 1;
  return counts;
}, { CIVIL_DEFENSE_SHELTER: 0, EMERGENCY_WATER: 0, AED: 0 });
