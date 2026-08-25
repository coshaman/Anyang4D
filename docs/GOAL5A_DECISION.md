# Goal 5A decision

## Decision

`AI_SURROGATE_B` · `ADMIN_AI_SCENARIO_SCREENING = DEMO_ONLY`

The model is useful for administrative triage and recovered the exact worst-scenario ranking well on this corpus, but it does not meet the frozen A requirement for stable primary-target error: assignment-cost P95 error remains high and OOD error is materially worse. Automatic operational screening is therefore disabled. The admin demo may show AI estimates only as shortlist aids, and exact reference verification remains mandatory.

## Evidence

- Corpus: 160 reproducible simulated administrative scenarios.
- Features: 28 pre-solver numeric features across scenario, demand, facility, graph, and spatial families.
- Split: grouped by scenario family and spatial hazard sector; multi-area/correlated and connectivity families held out as OOD.
- Selected model: Ridge with standardized inputs, selected on validation ranking.
- Validation ranking: Spearman 0.977020, NDCG@20 0.997453, Recall@20 0.95.
- Held-out test ranking: Spearman 0.979796, NDCG@20 0.997353, Recall@20 1.0.
- OOD ranking: Spearman 0.964430, NDCG@20 0.991946, Recall@20 0.85.
- Measured benchmark: 20 exact scenarios 30,910.94 ms; AI plus exact top-5 15,593.216 ms; measured 1.982× speedup and 15 exact calls avoided.

The high assignment-cost error and non-zero OOD regression error are the reasons this is not `AI_SURROGATE_A`. This decision does not authorize citizen guidance, flood prediction, observed-damage claims, or official forecasting.
