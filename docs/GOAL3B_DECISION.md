# SAFE-Twin Anyang Goal 3B decision

## 1. Hardware and environment

- Windows 11 build 10.0.26200, native execution
- Python 3.12.13, project `.venv` preserved
- 18 logical CPU threads, 16.67 GB physical RAM (2.73 GB available during final audit), approximately 20.27 GB free on the workspace disk at final audit
- WSL and Docker commands are available; NVIDIA GPU, `nvidia-smi`, CUDA runtime, and NVIDIA Container Toolkit path were not detected
- Hardware evidence: `artifacts/evals/ml/goal3b-hardware.json`

## 2. PhysicsNeMo

The selected research path was native CPU isolated `.venv-physicsnemo`, using official base packages only. Requested versions were PyTorch 2.13.0 and `nvidia-physicsnemo` 2.1.1. The install downloaded wheels but stalled during installation; two materially similar attempts were stopped. Import verification failed (`torch._C` DLL load failure; PhysicsNeMo not installed). Evidence: `artifacts/evals/ml/physicsnemo/environment.json`.

No further blind retries were made. The deterministic SAFE-Twin backend is therefore the recommended current backend. A Linux/NVIDIA environment with an approved driver/toolkit is the next legitimate PhysicsNeMo path.

## 3. Chosen architecture

`safetwin-deterministic-level-a-v1` is primary. It is transparent, CPU-capable, provenance-gated, and can accept future NGII terrain/rainfall without changing the contract. PhysicsNeMo remains an optional future surrogate; LarNO is not vendored or made a dependency.

## 4. Synthetic evaluation

The 16×16, six-timestep seed-7 synthetic pipeline produces time-varying `RELATIVE_HAZARD` frames. Baseline MAE/RMSE/IoU were `0.126813 / 0.156067 / 0.327485`; persistence comparator was `0.069619 / 0.089077 / 0.653061`. Temporal non-decrease was 1.0 for both. This is a pipeline and sanity result, not hydraulic validation or Anyang truth.

## 5. Anyang demo AOI and DEM request

Selected AOI: WGS84 bbox `126.946–126.966 E`, `37.376–37.396 N`; approximately 2×2 km. Selection evidence: 71 shelters, 10 water facilities, and 4,382 OSM nodes. Minimum latest 1 m records: `안양048 / 37612048`, `안양049 / 37612049`, `안양058 / 37612058`, `안양059 / 37612059`; all 2009, ASCII, 1 m, plane rectangular CRS, Incheon mean-sea-level datum, 0.25 m recorded accuracy. Details: `docs/NGII_DEM_DOWNLOAD_REQUEST.md`.

## 6. Current maturity and human blockers

Current maturity is `NONE` for real flood output because the selected raster bytes and official rainfall are absent. After raster plus scenario rainfall, the maximum target is Level A relative scenario hazard. Remaining human actions are NGII download/login, KMA or approved rainfall acquisition, and later Anyang flood observations/drainage/calibration for Level B/C.

## 7. Goal 4 decision

Goal 4 is **NOT AUTHORIZED**. Synthetic/benchmark frames are isolated to `/api/internal/simulations/*` and the internal lab. The minimum action to authorize a real Level-A hazard field is: download and audit the four NGII tiles, provide aligned rainfall (scenario is acceptable if clearly hypothetical), run the terrain/rainfall gate, and review the resulting provenance/limitations. Dynamic citizen routing still requires a separate safety/product decision after that field exists.

## 8. Verification

- Python: `\.venv\Scripts\python.exe -m pytest -q`
- Frontend unit tests: `npm test -- --pool=threads --poolOptions.threads.singleThread`
- Production build: `npm run build`
- Static checks: `npm run check:anti-slop`, `npm run check:secrets`
- Browser regression: `npx playwright test tests/e2e/goal2.spec.ts --workers=1`

The browser run reached `8/8 ok` across phone and desktop, including serious/critical axe checks, but the runner did not exit cleanly because repeated blocked OSM tile requests kept the Vite webserver teardown alive; it was manually interrupted after the passing test lines. This is recorded as a test-harness/network teardown limitation, not as evidence that an external map is available.

## 9. Next goal

Human action: obtain the four NGII raster tiles and a rainfall source. Then run Goal 3C: real Anyang Level-A terrain preprocessing and internal scenario review. Do not begin public dynamic routing until that review authorizes it.
