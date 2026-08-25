# Goal 4B performance evidence

Run:

```powershell
.venv\Scripts\python.exe scripts/evals/profile_goal4b.py
.venv\Scripts\python.exe scripts/evals/benchmark_goal4b.py
```

The optimization preserves exact deterministic min-cost flow semantics. It caches demand/facility snapping, active graphs by closed-road signature, STRtree hazard candidates, and serialized frame states by computational inputs. The latest measured artifact is `artifacts/evals/performance/goal4b-runtime-after.json`; the pre-optimization comparison is `goal4b-runtime-before.json`.

The cold compile is intentionally measured separately from cached timeline retrieval. A cold compile is bounded demo compilation work; interactive repeated frame retrieval is the cached path.
