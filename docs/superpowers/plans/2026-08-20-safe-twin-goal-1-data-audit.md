# SAFE-Twin Anyang Goal 1 Data Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Acquire and audit the real public datasets needed by SAFE-Twin Anyang, preserving raw evidence and making an evidence-backed Goal 3 flood-data decision without starting models or later product goals.

**Architecture:** A project-local Python environment runs a small standard-library-first acquisition tool. Each source adapter records official metadata, access outcome, raw bytes, SHA-256, schema/coverage observations, and explicit status in one manifest. Source-specific audit functions write normalized findings and blockers; no fetched raw file is mutated.

**Tech Stack:** Python 3.10+ project venv, `requests`, `pandas`, `pyproj`, `shapely`, `networkx`, optional `osmnx`, JSON/CSV/ZIP/XML parsing, OpenStreetMap Overpass/Geofabrik-compatible public sources where terms allow.

**Spec:** `C:\Users\owner\Documents\ChatGPT\Anyang\SAFE-Twin_Anyang_Codex_Pack\docs\GOALS.md` Goal 1 and the pasted Goal 1 requirements at `C:\Users\owner\.codex\attachments\fe445674-9134-4375-8b50-26a13b370015\pasted-text-1.txt`.

## Global Constraints

- Do not install project Python dependencies into the user/base interpreter; all commands use `.venv`.
- Download ordinary public files directly; request human action only for actual login, CAPTCHA, registration, key issuance, approval, license acceptance, or proprietary interactive download barriers.
- Preserve raw bytes unchanged under `data/raw/<provider>/<dataset>/` and record hash, timestamps, URLs, license, CRS, temporal coverage, and preprocessing status.
- Never invent Anyang counts, fields, capacities, population, flood labels, DEM resolution, or live weather values.
- Do not start LarNO, PhysicsNeMo, flood training, scenario routing, or Goal 2 implementation.

### Task 1: Isolated environment and acquisition contracts

**Files:**
- Modify: `pyproject.toml`, `.gitignore`, `.env.example`
- Create: `requirements.lock.txt`, `scripts/data/fetch_sources.py`, `scripts/data/audit_sources.py`
- Test: `tests/test_data_audit.py`

- [ ] Write failing tests for status validation, SHA-256 recording, and missing-key blocker formatting.
- [ ] Create `.venv`, install only project dependencies inside it, and run the failing tests there.
- [ ] Implement the smallest source-record and raw-download primitives.
- [ ] Re-run tests in `.venv` and verify API tests also use `.venv`.

### Task 2: Official source acquisition

**Files:**
- Modify: `data/manifests/data_manifest.json`
- Create: `data/raw/**`, `data/interim/**`, `docs/BLOCKED_DATA.md`

- [ ] Add adapters for all listed sources with official landing URLs and documented access requirements.
- [ ] Attempt each non-gated official download/API path and preserve successful raw responses.
- [ ] Record blocked/provider/schema failures and continue independent sources.

### Task 3: Coverage and quality audit

**Files:**
- Create: `docs/DATA_QUALITY_REPORT.md`, `scripts/data/report_quality.py`, `artifacts/evals/data/**`
- Modify: `docs/PROGRESS.md`

- [ ] Inspect real columns/records and compute Anyang counts, null/invalid rates, geometry quality, CRS, and temporal metadata.
- [ ] Audit OSM pedestrian graph, DEM candidates, land cover, spatial population, flood traces, and weather readiness.
- [ ] Write explicit DEM Level A/B/C verdicts and Goal 3 flood-data verdict.
- [ ] Run the complete acquisition/audit command in `.venv` and record exact output, blockers, and artifacts.

