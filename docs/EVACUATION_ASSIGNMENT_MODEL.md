# Capacity-constrained evacuation assignment

The deterministic solver uses a min-cost flow network. Demand units supply the official 2026-07-31 Anyang administrative-dong population totals; their coordinates are labeled `SIMULATED_SPATIAL_ALLOCATION`, not a census grid. Eligible available facilities receive flow up to effective capacity; a high-penalty unserved arc preserves conservation when demand is unreachable or capacity is insufficient.

Invariants:

- `assigned + unserved = total_demand`;
- facility assignment never exceeds effective capacity;
- closed/unavailable facilities receive zero;
- disconnected demand remains explicitly unserved;
- only disaster-eligible facility categories are destinations;
- assignment is deterministic for identical scenario/data inputs.

Costs are OSM walking-network shortest-path metres. Bottlenecks are reported as `대피 경로 집중 구간` based on assigned flow through graph edges; the engine makes no crowd-density or crush-risk claim.
