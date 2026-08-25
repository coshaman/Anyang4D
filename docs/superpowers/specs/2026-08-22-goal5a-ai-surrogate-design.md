# Goal 5A AI surrogate design

## Decision

Build an admin-only, CPU-only tabular surrogate around the frozen Goal 4B engine. The exact engine remains the only authority for labels and displayed final values. The surrogate estimates interpretable reference outputs to prioritize explicit simulated administrative scenarios, then exact-verifies a bounded top-K.

## Model strategy

Use scikit-learn only. Compare a median baseline, Ridge, and HistGradientBoosting regressors wrapped per target. Select one model family by held-out multi-target error plus worst-case ranking recovery, not by a subjective score. Store direct targets: `assigned`, `unserved`, `assignment_cost`, `available_capacity_deficit`, and `overloaded_shelter_count`. Derive the ranking score transparently from exact labels as `unserved + 0.25 * overloaded_shelter_count + 0.001 * assignment_cost`; this is a triage formula, not a real-world risk score.

## Data flow

`SIMULATED_ADMIN_SCENARIO` generator → pre-solver feature extractor → frozen exact engine → `REFERENCE_SIMULATION_LABEL` JSONL/checkpoint → grouped split → baseline/model evaluation → versioned model bundle → screening API → exact top-K verification.

The feature extractor may resolve explicit scenario state and static graph descriptors, but it must not consume assignment or post-solve fields. Local and national shelter records are never combined into a second operational facility list; the AI uses the same canonical facility set as Goal 4B and records source provenance in metadata.

## Leakage and support

Splits are grouped by scenario family and spatial sector. A held-out OOD group contains multi-area hazards plus high-capacity shelter closures and correlated road/facility failures. Inference fails closed when feature schema/model version differs or standardized feature distance exceeds the training support threshold. The result is `AI_ESTIMATE_UNSUPPORTED`, which requires exact computation.

## Product boundary

Only `/api/admin/goal5a` is exposed. No citizen route, forecast, flood-depth, terrain, or real-disaster endpoint consumes the model. The admin UI distinguishes `AI_SURROGATE_ESTIMATE` from `REFERENCE_SIMULATION_LABEL`; exact verification changes `exact_verified` to true and makes exact values authoritative.

## Initial corpus

Generate 160 deterministic candidates across light, moderate, capacity, connectivity, localized, multi-area, high-participation, and correlated-disruption families. Checkpoint each label and resume by scenario ID. Increase only if the measured generalization gap indicates undercoverage.
