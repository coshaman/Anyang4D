from __future__ import annotations

import json
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from services.api.goal4a import STORE, _ensure_presets, _frame_payload, clear_computation_caches

_ensure_presets()
scenario = STORE.get("anyang-flood-style-admin")
times = scenario.frame_times()

def measure(callable_, repetitions: int) -> list[float]:
    values = []
    for _ in range(repetitions):
        started = time.perf_counter()
        callable_()
        values.append((time.perf_counter() - started) * 1000)
    return values


ab_scenario = STORE.get("anyang-civil-defense-outage")
cold_compile_samples = []
for _ in range(3):
    clear_computation_caches()
    cold_compile_samples.append(measure(lambda: [_frame_payload(scenario, minute) for minute in times], 1)[0])
clear_computation_caches()
_ = [_frame_payload(scenario, minute) for minute in times]
_ = [_frame_payload(ab_scenario, minute) for minute in ab_scenario.frame_times()]
tracemalloc.start()
cached_retrieval = measure(lambda: _frame_payload(scenario, times[1]), 10)
ab = measure(lambda: (_frame_payload(scenario, 20), _frame_payload(ab_scenario, 20)), 5)
_, peak_memory = tracemalloc.get_traced_memory()
current, _ = tracemalloc.get_traced_memory()
tracemalloc.stop()

def stats(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {"median_ms": round(statistics.median(values), 3), "p90_ms": round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.9))], 3), "p95_ms": round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))], 3), "max_ms": round(max(values), 3)}

artifact = {
    "scenario_id": scenario.scenario_id,
    "same_bounded_demo_aoi": True,
    "cold_compile": {"frame_count": len(times), "timings_ms": cold_compile_samples, "summary": stats(cold_compile_samples)},
    "cached_timeline_frame_retrieval": {"repetitions": len(cached_retrieval), "summary": stats(cached_retrieval)},
    "compiled_ab_compare": {"repetitions": len(ab), "summary": stats(ab)},
    "memory": {"peak_traced_bytes": peak_memory, "retained_traced_bytes": current},
    "optimization": ["cached demand/facility snaps", "cached active graph by closed-road signature", "STRtree hazard candidate filtering", "state-payload cache keyed by actual computational state"],
    "semantic_policy": "exact deterministic NetworkX min-cost flow; no approximation",
}
out = ROOT / "artifacts/evals/performance/goal4b-runtime-after.json"
out.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(artifact, ensure_ascii=False))
