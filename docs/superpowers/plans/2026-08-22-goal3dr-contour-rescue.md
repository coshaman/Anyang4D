# Goal 3D-R Contour-Aware Terrain Rescue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Perform one final bounded contour-aware reconstruction attempt against the already-frozen Goal 3D validation contract, compare it fairly with the previous IDW surface, and permanently stop the terrain-rescue branch if no method reaches `TERRAIN_B`.

**Architecture:** Freeze and hash the existing validation plan first. Audit actual DXF contour topology, create leakage-safe spatial groups, evaluate a contour-aware distance surface and a small regularized alternative when dependencies permit, optionally record constrained TIN as not run, then compare all methods on identical holdouts, seam, source-support, and hydrologic diagnostics. No downstream flood or routing code is called.

**Tech Stack:** Python, NumPy, existing DXF parser, Shapely if useful, optional GRASS/QGIS only if already available, Rasterio for artifact inspection, pytest, JSON/GeoTIFF artifacts.

**Spec:** The user-provided Goal 3D-R specification in `docs`/pasted request, with `docs/TERRAIN_VALIDATION_PLAN.md` as immutable acceptance criteria.

## Global Constraints

- Hash the pre-existing validation plan before any new interpolation result is generated.
- Do not change thresholds, shrink the AOI, drop difficult samples, or reinterpret old IDW as successful.
- Use the same final holdout IDs and road-support definition for baseline and rescue candidates.
- Treat contours as isolines, not independent random points; use 25m spatial-block holdouts.
- Record unavailable external methods with an explicit reason; do not install obscure dependencies merely to force a candidate.
- Do not run rainfall, flood simulation, hazard frames, Goal 4, citizen routing, or PhysicsNeMo.
- If no method passes the frozen gate, record `TERRAIN_C`, `STREET_LEVEL_FLOOD_TERRAIN_PATH=DROP`, and `CITIZEN_HAZARD_ROUTING_FROM_TERRAIN=DROP` permanently for this project.

## Tasks

- [ ] Hash the frozen plan and capture Goal 3D baseline evidence under `artifacts/evals/terrain/goal3dr/`.
- [ ] Add failing tests, then implement DXF contour topology audit: intervals, constancy, crossings, dangling endpoints, closed/duplicate contours, boundary continuation, and ordering anomalies.
- [ ] Add failing tests, then implement shared spatial holdout IDs and contour-aware distance interpolation without independent-vertex IDW semantics.
- [ ] Add failing tests, then implement a bounded RST/equivalent adapter or record `METHOD_B_NOT_RUN` with environment evidence; record constrained TIN availability as Method C.
- [ ] Run baseline plus rescue methods on identical samples; write per-method artifacts and the comparison table including runtime/memory.
- [ ] Compute per-method source road support separately from model coverage and hydrologic diagnostics.
- [ ] Apply the frozen decision logic and write `docs/TERRAIN_RESCUE_METHODS.md`, `docs/GOAL3D_RESCUE_DECISION.md`, and the required JSON artifacts.
- [ ] Run all tests, build, anti-slop, secrets, and artifact-readability checks; stop without starting another rescue.

## Verification Gates

No candidate can be promoted unless it satisfies the original `TERRAIN_A`/`TERRAIN_B` rules, uses identical holdouts, has defensible contour assumptions, acceptable seam/morphology, and preserves source-support limitations. A failed rescue remains diagnostic only.

