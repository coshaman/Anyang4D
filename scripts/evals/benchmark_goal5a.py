from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from services.ai_surrogate.dataset import load_rows
from services.ai_surrogate.explain import explain_features
from services.ai_surrogate.model import load_bundle, predict_bundle
from services.api.goal4a import _frame_payload, clear_computation_caches
from services.simulator.contracts import Scenario


def samples(callable_, repetitions: int) -> list[float]:
    values = []
    for _ in range(repetitions):
        started = time.perf_counter(); callable_(); values.append((time.perf_counter() - started) * 1000)
    return values


def summary(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {"median_ms": round(statistics.median(values), 3), "p95_ms": round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))], 3), "throughput_per_second": round(1000 / max(statistics.median(values), 1e-9), 3)}


def main() -> None:
    rows = load_rows()
    bundle = load_bundle(Path("models/scenario_triage/model.joblib"))
    n = min(20, len(rows))
    selected = rows[:n]
    ai_times = samples(lambda: [predict_bundle(bundle, row["scenario_id"], row["features"], explain_features(row["features"], bundle["metadata"])) for row in selected], 5)
    scenarios = [Scenario.from_dict(row["scenario"]) for row in selected]
    clear_computation_caches()
    exact_times = samples(lambda: [_frame_payload(scenario, scenario.frame_times()[-1]) for scenario in scenarios], 1)
    clear_computation_caches()
    top_k = min(5, n)
    started = time.perf_counter()
    predictions = [predict_bundle(bundle, row["scenario_id"], row["features"]) for row in selected]
    ranked = sorted(predictions, key=lambda item: item.ranking_score or float("-inf"), reverse=True)[:top_k]
    verified = [_frame_payload(scenarios[selected.index(next(row for row in selected if row["scenario_id"] == item.scenario_id))], scenarios[selected.index(next(row for row in selected if row["scenario_id"] == item.scenario_id))].frame_times()[-1]) for item in ranked]
    hybrid_ms = (time.perf_counter() - started) * 1000
    artifact = {"scenario_count": n, "top_k": top_k, "ai_batch": summary(ai_times), "exact_all": summary(exact_times), "ai_plus_exact_top_k": {"elapsed_ms": round(hybrid_ms, 3), "scenarios_per_second": round(1000 * n / max(hybrid_ms, 1e-9), 3)}, "speedup_exact_all_vs_hybrid": round((exact_times[0] / hybrid_ms), 3), "exact_solver_calls_avoided": max(0, n - top_k), "exact_reference": "goal4b-exact-reference-v1"}
    output = Path("artifacts/evals/performance/goal5a/runtime.json"); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, ensure_ascii=False))


if __name__ == "__main__":
    main()
