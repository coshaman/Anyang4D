export const PROVENANCE = [
  "OFFICIAL",
  "SIMULATED",
  "OBSERVED_AI",
  "STALE_OR_UNKNOWN"
] as const;

export type Provenance = (typeof PROVENANCE)[number];

export type ProvenanceLine = {
  provenance: Provenance;
  label: string;
  detail: string;
  fixture?: boolean;
};
