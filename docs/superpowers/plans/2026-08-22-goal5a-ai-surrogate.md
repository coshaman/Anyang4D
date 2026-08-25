# Goal 5A AI Surrogate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CPU-only administrative scenario surrogate that ranks explicit simulated scenarios and exact-verifies the shortlist without changing Goal 4B semantics.

**Architecture:** Add an isolated `services/ai_surrogate` package. It consumes pre-solver features from the existing graph/scenario inputs, receives labels only from the existing exact frame engine, and exposes only `/api/admin/goal5a`. Persist JSONL dataset/checkpoints, grouped split manifests, metrics, and a versioned joblib model bundle.

**Tech Stack:** Python 3.11, scikit-learn, NumPy, joblib, existing FastAPI/httpx/pytest, React/TypeScript/Vitest/Playwright.

**Spec:** `docs/superpowers/specs/2026-08-22-goal5a-ai-surrogate-design.md`, `docs/AI_SURROGATE_VALIDATION_PLAN.md`

## Global Constraints

- `FINAL_TERRAIN_CLASS = TERRAIN_C`.
- `STREET_LEVEL_FLOOD_TERRAIN_PATH = DROP`.
- `CITIZEN_HAZARD_ROUTING_FROM_TERRAIN = DROP`.
- AI terminology is scenario screening/simulation surrogate only; never forecast, damage prediction, flood probability, or citizen guidance.
- Goal 4B exact engine files keep their semantics; AI labels use `REFERENCE_SIMULATION_LABEL`.
- No GPU, neural network, PhysicsNeMo, flood depth, LLM, or citizen endpoint.
- Exact verification is mandatory for displayed final values; `exact_verified` defaults false.
- Validation thresholds are frozen in `docs/AI_SURROGATE_VALIDATION_PLAN.md` before held-out evaluation.

---

### Task 1: Dependency and isolated package contract

**Files:**
- Modify: `pyproject.toml`
- Create: `services/ai_surrogate/__init__.py`, `services/ai_surrogate/contracts.py`, `tests/test_goal5a_contracts.py`

**Interfaces:**
- Produce `SurrogatePrediction`, `ScreeningCandidate`, `ExactVerification` typed dictionaries/dataclasses.
- Produce model bundle metadata with `model_version`, `feature_schema_version`, `reference_engine_version`, and `exact_verified`.

- [ ] Add pinned `scikit-learn` and `joblib` dependencies.
- [ ] Write tests for default `exact_verified=False`, provenance values, and fail-closed schema mismatch.
- [ ] Run `.venv\Scripts\pytest.exe tests/test_goal5a_contracts.py -q` and install the pinned CPU dependencies if absent.

### Task 2: Scenario generator and pre-solver features

**Files:**
- Create: `services/ai_surrogate/scenarios.py`, `services/ai_surrogate/features.py`, `scripts/ai/generate_goal5a_dataset.py`
- Create: `tests/test_goal5a_generation.py`, `tests/test_goal5a_features.py`

**Interfaces:**
- `generate_candidates(seed: int, count: int) -> list[Scenario]`.
- `extract_features(scenario: Scenario) -> dict[str, float]`.

- [ ] Generate 160 candidates across the eight documented failure families, using actual roads/facilities and deterministic seeds.
- [ ] Include family, spatial sector, closure severity, and seed metadata without using post-solve targets.
- [ ] Compute static graph descriptors once and aggregate removed-edge counts/length/betweenness/bridge flags.
- [ ] Add deterministic ID and duplicate tests plus target-feature leakage audit.

### Task 3: Exact label corpus with checkpoint/resume

**Files:**
- Create: `services/ai_surrogate/dataset.py`, `tests/test_goal5a_dataset.py`
- Modify: `scripts/ai/generate_goal5a_dataset.py`
- Create: `data/derived/ai_scenario_surrogate/README.md`

**Interfaces:**
- `generate_labels(candidates, output_dir, resume=True) -> DatasetManifest`.
- Each JSONL row contains scenario JSON, seed, feature schema, source hashes, state signatures, exact outputs, runtime, and `REFERENCE_SIMULATION_LABEL`.

- [ ] Call only `_frame_payload`/exact assignment for labels; never write AI values as labels.
- [ ] Resume by scenario ID and verify source/reference hashes before reuse.
- [ ] Add source/version retention and label-provenance tests.

### Task 4: Grouped splits, baselines, model candidates, OOD, ablation

**Files:**
- Create: `services/ai_surrogate/evaluate.py`, `scripts/ai/train_goal5a.py`, `scripts/ai/evaluate_goal5a.py`
- Create: `tests/test_goal5a_evaluation.py`
- Create: `artifacts/evals/ai/goal5a/`

**Interfaces:**
- `build_grouped_split(rows) -> SplitManifest`.
- `train_and_evaluate(dataset, split) -> EvaluationArtifact`.

- [ ] Split by scenario family + spatial sector; hold out multi-area/correlated/high-capacity closure OOD groups.
- [ ] Evaluate median, Ridge, and HistGradientBoosting candidates on validation only.
- [ ] Report regression, ranking, family-band errors, OOD, and public-data ablations.
- [ ] Freeze model selection from validation, then write held-out metrics without changing thresholds.

### Task 5: Versioned model bundle, support check, explanations, inference

**Files:**
- Create: `services/ai_surrogate/model.py`, `services/ai_surrogate/explain.py`, `scripts/ai/infer_goal5a.py`
- Create: `models/scenario_triage/README.md`
- Create: `tests/test_goal5a_model.py`

**Interfaces:**
- `load_bundle(path)`, `predict(features)`, `support_status(features)`, `explain(features) -> list[FeatureContribution]`.

- [ ] Persist model, feature schema, training IDs, split IDs, source hashes, dependency versions, seeds, metrics, and license metadata.
- [ ] Fail closed on missing features, version mismatch, and support distance/range violations.
- [ ] Return deterministic feature-level “주요 입력” explanations; never causal language.

### Task 6: Bulk screening and exact top-K API

**Files:**
- Create: `services/api/goal5a.py`, `tests/test_goal5a_screening_api.py`
- Modify: `services/api/main.py`

**Interfaces:**
- `POST /api/admin/goal5a/screen` accepts base scenario + candidate count + top_k.
- `POST /api/admin/goal5a/verify/{scenario_id}` returns AI estimate plus exact authoritative result.

- [ ] Generate candidates → infer/rank → exact-verify top-K → retain both outputs.
- [ ] Return `AI_ESTIMATE_UNSUPPORTED` and require exact computation for unsupported candidates.
- [ ] Ensure no citizen route imports or endpoints consume the surrogate.
- [ ] Test ranking, top-K verification, exact ordering, provenance, and fail-closed behavior.

### Task 7: Admin-only UI and demo flow

**Files:**
- Modify: `apps/web/src/AdminSimulator.tsx`, `apps/web/src/App.tsx`, `apps/web/src/styles.css`
- Modify: `tests/e2e/goal4a.spec.ts`
- Create: `tests/e2e/goal5a.spec.ts`

**Interfaces:**
- `/admin?demo=1` adds “AI 대규모 시나리오 선별”; ordinary citizen routes remain unchanged.

- [ ] Show candidate count, AI estimate, support state, exact verification state, top-K, and explanation.
- [ ] On selection, call exact verification and render exact values as authoritative while preserving estimates.
- [ ] Add mitigation A/B action through existing exact scenario controls.
- [ ] Add keyboard, large text, reduced-motion, axe, and visual E2E coverage.

### Task 8: Documentation, benchmark, claim audit, final gate

**Files:**
- Create: `docs/AI_SCENARIO_DATASET.md`, `docs/AI_SCENARIO_FEATURES.md`, `docs/AI_SCENARIO_EVALUATION.md`, `docs/AI_SCREENING_ARCHITECTURE.md`, `docs/model_cards/anyang-scenario-triage.md`
- Modify: `docs/COMPETITION_DEMO_FLOW.md`, `docs/GOAL5A_DECISION.md`, `docs/DATA_AND_LICENSES.md`, `THIRD_PARTY_NOTICES.md`, `docs/PROGRESS.md`
- Create: `scripts/evals/audit_goal5a_claims.py`, `scripts/evals/benchmark_goal5a.py`

- [ ] Record exact corpus count/runtime, split, features, model/license, metrics, OOD, ablation, throughput, speedup, calls avoided, and failure modes.
- [ ] Classify only from frozen criteria as `AI_SURROGATE_A/B/C` and set `ADMIN_AI_SCENARIO_SCREENING` accordingly.
- [ ] Run full pytest, Vitest, build, Playwright, axe, anti-slop, secrets, boundary/claim audit, and benchmark.

