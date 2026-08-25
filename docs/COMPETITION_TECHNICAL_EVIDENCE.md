# SAFE-Twin Anyang technical evidence

## Public data

- National filtered civil-defense shelters: 231; retrieved 2026-08-20.
- National filtered emergency-water records: 71; retrieved 2026-08-20.
- Anyang AED file: 305 records, source date 2025-12-22, retrieved 2026-08-20; source contains no coordinates.
- Local Anyang shelter context: 224; local emergency-water context: 46; response-material records: 33.
- Official Anyang resident population: 31 administrative-dong units, 562,143 people, reference date 2026-07-31. Coordinates are simulated demo anchors because the workbook has no dong polygons.
- OSM bounded demo graph: 16,745 nodes and 19,439 edges in the release readiness check; ODbL attribution is required.

Evidence artifact: `artifacts/evals/release/data-consistency.json`.

## Exact 4D engine

Goal 4B uses a deterministic scenario state model with time-keyed hazard geometry, road closures, facility availability/capacity events, demand participation assumptions, and exact NetworkX min-cost flow assignment. A/B comparison is calculated from two persisted `ADMIN_SCENARIO` definitions. The fixed release B variant keeps the same area and closes one high-load shelter; measured delta is available shelters `-1`, assignment cost `+1,001,955.9 m`, assigned/unserved delta `0` in that run.

## AI surrogate

Goal 5A uses 160 simulated administrative scenarios, 28 pre-solver features, grouped train/validation/test/OOD splits, and a standardized Ridge multi-output model. Validation ranking Spearman is 0.977020; OOD ranking Spearman is 0.964430 and Recall@20 is 0.85. The decision remains `AI_SURROGATE_B`; screening is `DEMO_ONLY`. AI output is never authoritative and exact top-K verification is mandatory.

Measured CPU scale: N=20, 100, 160, and 500 were run with actual feature generation, AI inference, and exact top-5 verification. N=1000 was not measured because deterministic feature extraction exceeded a practical release benchmark window; no extrapolation is reported. Same-run N=20 exact-all was 32,167.964 ms and AI+exact top-5 was 18,033.545 ms, a conservative measured 1.78x speed claim.

## Quality and limits

- Release readiness: backend, OSM demo graph, facilities, population, scenario engine, exact solver, and AI model all reported ready.
- Real HTTP smoke: `/admin?demo=1`, official state, frame, fixed A/B, AI screen, exact verification, frontend load all passed; exact result was authoritative.
- Real browser capture: admin usable in 1,466 ms warm route load; A/B 579 ms in the final capture sequence; conservative representative AI 100-candidate screen plus exact verification 24,889 ms; latest warm repetition 12,408 ms; cold `start_demo.ps1` on a separate port 15,380 ms. These are local one-run measurements, not hosted SLAs.
- Playwright capture used aborted OSM tile requests and retained layout/vector/data panels, so network failure did not crash the demo.
- Accessibility gate includes axe serious/critical violation checks, keyboard interactions, reduced-motion, large-text, 200% zoom, and phone/desktop E2E coverage.

## Final release boundary

The high-resolution DEM acquisition branch is permanently closed for this release. The supplied native 90 m raster remains provenance evidence and, if shown at all, is coarse terrain context only. It is not used for flood depth, road closure inference, citizen routing, or safety decisions. The release product therefore does not depend on 1 m/5 m DEM availability. `FLOOD` is an administrative What-if meaning `가정 침수영역에 따른 영향 시뮬레이션`, not physical flood prediction.

Limits: terrain class remains `TERRAIN_C`; terrain-derived flood path is dropped; no citizen dynamic emergency routing; population spatial allocation is simulated; AI is demo-only; no official real-time hazard forecast.
