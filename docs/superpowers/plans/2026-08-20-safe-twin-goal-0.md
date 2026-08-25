# SAFE-Twin Anyang Goal 0 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a runnable SAFE-Twin Anyang repository foundation with explicit provenance, safety-aware copy, and a responsive map-first citizen/admin shell.

**Architecture:** A small Vite React TypeScript web app provides `/`, `/simulate`, `/admin`, and `/about-data` views. A Python FastAPI service exposes a typed provenance contract and fixture-only foundation endpoints. Shared behavior is tested at the API and UI boundaries; fixture content is visibly labeled and never presented as live public data.

**Tech Stack:** React 18, TypeScript, Vite, Vitest, Playwright, Python 3.11+, FastAPI, Pydantic, pytest, plain CSS variables.

**Spec:** `SAFE-Twin_Anyang_Codex_Pack/docs/GOALS.md` Goal 0, with `AGENTS.md`, `docs/PRODUCT_SPEC.md`, `docs/SAFETY_AND_CLAIMS.md`, `docs/DESIGN_SYSTEM.md`, and `docs/ARCHITECTURE.md` as binding product requirements.

## Global Constraints

- Every dynamic datum uses exactly one provenance value: `OFFICIAL`, `SIMULATED`, `OBSERVED_AI`, or `STALE_OR_UNKNOWN`.
- Fixture data is visibly marked and is not silently substituted for public data.
- Citizen copy must not claim safety, certainty, or current official status from fixtures.
- Primary targets are at least 48px, body text is at least 17px, and official/simulation meaning is not conveyed by color alone.
- No decorative AI badges, sparkle/robot/brain/magic icons, neon gradients, glassmorphism, glow, or fake confidence.
- No secrets are committed; `.env.example` contains names only.

### Task 1: Repository foundation

**Files:**
- Create: `package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`
- Create: `apps/web/*`, `packages/contracts/*`
- Create: `services/api/*`, `tests/*`
- Create: `.env.example`, `.gitignore`, `pyproject.toml`

- [ ] Write the failing provenance contract/API tests.
- [ ] Run the focused tests and confirm failure because the modules/endpoints do not exist.
- [ ] Add the minimal typed contracts and FastAPI endpoints.
- [ ] Run API and TypeScript tests and confirm they pass.

### Task 2: Map-first web experience

**Files:**
- Create: `apps/web/src/App.tsx`, `apps/web/src/styles.css`, `apps/web/src/main.tsx`
- Test: `apps/web/src/App.test.tsx`
- Create: `playwright.config.ts`, `tests/e2e/foundation.spec.ts`

- [ ] Write a failing UI test for Korean navigation, fixture disclosure, provenance text, and large-text mode.
- [ ] Run the UI test and confirm the expected missing-shell failure.
- [ ] Implement the responsive citizen/admin shell with accessible controls and fixture-only map illustration.
- [ ] Run Vitest and Playwright at phone and desktop sizes.

### Task 3: Safety and repository guards

**Files:**
- Create: `scripts/check_anti_slop.py`, `scripts/check_secrets.py`
- Create: `THIRD_PARTY_NOTICES.md`, `docs/PROGRESS.md`, `docs/BLOCKED_DATA.md`
- Create: `data/raw/.gitkeep`, `data/interim/.gitkeep`, `data/processed/.gitkeep`, `data/manifests/data_manifest.json`, `artifacts/evals/.gitkeep`, `models/.gitkeep`

- [ ] Add source checks for forbidden decorative AI language/effects and committed secrets.
- [ ] Run both checks against the repository.
- [ ] Record exact commands, results, screenshots, and remaining unvalidated assumptions in `docs/PROGRESS.md`.

