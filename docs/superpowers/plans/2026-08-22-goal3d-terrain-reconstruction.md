# Goal 3D Terrain Reconstruction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruct a deterministic, provenance-preserving computational terrain surface for the Anyang demo AOI from the newly acquired 2025 NGII 1:1,000 DXF tiles, and rigorously validate it without running flood simulation.

**Architecture:** Parse only semantically defensible elevation-bearing DXF entities into immutable constraints, build one or more deterministic surface candidates on a declared computational grid, validate with spatially grouped holdouts and seam/road-support diagnostics, then publish one canonical raster plus machine-readable provenance and quality reports. The output remains terrain evidence, not a flood hazard result.

**Tech Stack:** Python, existing project test runner, NumPy, Shapely, PyProj, Rasterio where available, pure ASCII DXF group-code parsing, GeoJSON/JSON/GeoTIFF artifacts.

**Spec:** Current 2025 DXF/XML metadata and the existing demo AOI are authoritative. Main AOI coverage is supplied by sheets 37612048 and 37612049; 37612058 and 37612059 are boundary-context sheets. Historical/90m IMG files are reference-only and cannot be upsampled as street-level terrain.

## Global Constraints

- Write and freeze `docs/TERRAIN_VALIDATION_PLAN.md` before inspecting final reconstruction metrics.
- Use TDD: each production module starts with a failing focused test.
- Preserve source sheet, layer, entity handle, geometry, elevation, CRS, and source hashes in every derived artifact.
- Do not run flood simulation, hazard-frame generation, Goal 4 routing, citizen routing, or PhysicsNeMo.
- If no candidate satisfies the frozen criteria, publish diagnostics and classify the terrain as `TERRAIN_C`; do not relax criteria or manufacture confidence.
- Keep the existing invalid 90m DEM evidence explicitly excluded from high-resolution terrain.

## Tasks

- [x] Freeze the validation contract and expected artifact schema in `docs/TERRAIN_VALIDATION_PLAN.md`.
- [x] Add failing tests, then implement `services/terrain/contracts.py` and `services/terrain/dxf.py` for semantic DXF layer auditing and extraction of contour/spot constraints.
- [x] Implement support-density and constraint-quality diagnostics in `services/terrain/support.py` and the Goal 3D runner.
- [x] Add failing tests, then implement deterministic constrained surface candidates in `services/terrain/interpolation.py`.
- [x] Add failing tests, then implement grouped holdout, contour, seam, slope, sink, and flow diagnostics in `services/terrain/validation.py`.
- [x] Add failing tests, then implement road-corridor support diagnostics in `services/terrain/road_support.py` and the Goal 3D runner.
- [x] Add failing tests, then implement canonical terrain generation and dry-run loading in `scripts/evals/goal3d_terrain.py` and `services/terrain/loader.py`.
- [x] Produce the canonical GeoTIFF, provenance, quality, support, and diagnostic artifacts; update manifest and Goal 3D documentation.
- [x] Run focused tests, full tests, frontend checks, build, anti-slop, and secrets checks; verify no flood simulation was run.

## Verification Gates

Each task must pass its focused tests before the next implementation task. The final gate requires the frozen validation plan, source hashes, AOI/sheet reconciliation, quality class, authorization flags, canonical artifact readability, and complete test/build evidence in `docs/PROGRESS.md`.
