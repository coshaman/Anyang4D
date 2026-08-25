# Model card: Anyang scenario triage surrogate

## Purpose

CPU-only tabular surrogate for rapidly prioritizing explicit `SIMULATED_ADMIN_SCENARIO` combinations before exact administrative what-if verification.

## Non-purpose

It is not a disaster predictor, damage predictor, flood-depth model, probability model, official forecast, safe-route generator, or citizen emergency feature. Terrain remains `TERRAIN_C`; terrain-derived flood and citizen routing remain dropped.

## Labels and data

160 scenarios were generated from the real bounded OSM graph, official Anyang population totals, and the same canonical shelter semantics as Goal 4B. Labels were generated only by `goal4b-exact-reference-v1` and stored as `REFERENCE_SIMULATION_LABEL`. Local/national crosswalk records were not duplicated into the operational facility list.

## Features and split

The bundle uses 28 pre-solver features. Grouped splitting combines scenario family and hazard spatial sector. Multi-area/correlated and connectivity families are held out as OOD. No post-solve assignment, load, unserved, travel-cost, or bottleneck field is a feature.

## Model and license

The selected model is standardized Ridge from scikit-learn 1.6.1, serialized with joblib 1.4.2. scikit-learn is BSD-3-Clause; joblib is BSD-3-Clause. No third-party weights are used.

## Results

Validation ranking was Spearman 0.977020, NDCG@20 0.997453, Recall@20 0.95. Held-out ranking was Spearman 0.979796, NDCG@20 0.997353, Recall@20 1.0. OOD ranking was Spearman 0.964430, NDCG@20 0.991946, Recall@20 0.85. Assignment-cost P95 error was high, so the operational classification is `AI_SURROGATE_B` and the product setting is `ADMIN_AI_SCENARIO_SCREENING = DEMO_ONLY`.

## Safety and failure modes

Feature schema/version mismatch and support-range violations return `AI_ESTIMATE_UNSUPPORTED`. Exact verification is required for every selected result; `exact_verified` starts false and exact values are authoritative after verification. Known weaknesses are assignment-cost heavy-tail error, OOD extrapolation, and simulated scenario distribution bias.
