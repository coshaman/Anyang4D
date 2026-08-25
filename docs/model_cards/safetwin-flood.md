# SAFE-Twin flood engine model card

## Current status

The shipped backend is `safetwin-deterministic-level-a-v1`. Current generated demo frames are `SYNTHETIC`, `RELATIVE_HAZARD`, and Level A. They are not water depth, flood probability, emergency-grade guidance, or Anyang observations.

The engine is ready to accept `ANYANG_OFFICIAL` terrain and `SCENARIO` rainfall once the NGII raster is downloaded and audited. Official weather mode requires verified rainfall data. Level B requires Anyang flood labels; Level C requires drainage/inlet/sewer topology and calibration observations.

## Inputs and assumptions

- DEM grid with CRS, transform, resolution, nodata
- Scenario rainfall in millimetres per timestep
- Lower relative elevation and local depression increase the relative field
- Rainfall accumulates without a recession term
- No underground drainage, sewer, inlet, building blockage, roughness, or calibration

## Provenance classes

- `SYNTHETIC`: current internal demo fixture
- `BENCHMARK`: future external benchmark evaluation only
- `ANYANG_OFFICIAL`: real Anyang source files, still gated by fidelity level
- `FUTURE_ANYANG`: reserved migration/provenance marker, not current evidence

## Safety

The API rejects `WATER_DEPTH_M` below Level C and rejects synthetic/benchmark depth output. No route recommender consumes simulation frames.
