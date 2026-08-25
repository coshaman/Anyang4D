from __future__ import annotations

import json
import statistics
import time
import tracemalloc
from pathlib import Path

from services.ai_surrogate.explain import explain_features
from services.ai_surrogate.features import extract_features
from services.ai_surrogate.model import load_bundle, predict_bundle
from services.ai_surrogate.scenarios import generate_candidates
from services.api.goal4a import _frame_payload, clear_computation_caches
from services.simulator.contracts import Scenario


ROOT = Path(__file__).resolve().parents[2]
SIZES = (20, 100, 160, 500)
TOP_K = 5


def median_summary(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {"median_ms": round(statistics.median(values), 3), "p95_ms": round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))], 3), "throughput_per_second": round(1000 / max(statistics.median(values), 1e-9), 3)}


def timed(callable_):
    started = time.perf_counter()
    result = callable_()
    return result, (time.perf_counter() - started) * 1000


def main() -> None:
    bundle = load_bundle(ROOT / "models/scenario_triage/model.joblib")
    results = []
    for size in SIZES:
        candidates, generation_ms = timed(lambda size=size: generate_candidates(seed=5, count=size))
        feature_values, feature_ms = timed(lambda: [extract_features(scenario) for scenario in candidates])
        rows = list(zip(candidates, feature_values))
        inference_runs = []
        peak_mb = 0.0
        predictions = []
        for _ in range(3):
            tracemalloc.start()
            predicted, elapsed = timed(lambda: [predict_bundle(bundle, scenario.scenario_id, features, explain_features(features, bundle["metadata"])) for scenario, features in rows])
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            predictions = predicted
            inference_runs.append(elapsed)
            peak_mb = max(peak_mb, peak / 1024 / 1024)
        supported = sum(prediction.ranking_score is not None for prediction in predictions)
        ranked = sorted(zip(candidates, predictions), key=lambda pair: pair[1].ranking_score if pair[1].ranking_score is not None else float("-inf"), reverse=True)[:TOP_K]
        clear_computation_caches()
        exact_started = time.perf_counter()
        exact_results = [_frame_payload(scenario, scenario.frame_times()[-1]) for scenario, _ in ranked]
        exact_topk_ms = (time.perf_counter() - exact_started) * 1000
        exact_all = {"measured": False, "reason": "skipped beyond N=20 to avoid unnecessary exact-solver cost"}
        if size == 20:
            clear_computation_caches()
            exact_all_started = time.perf_counter()
            _ = [_frame_payload(scenario, scenario.frame_times()[-1]) for scenario in candidates]
            exact_all = {"measured": True, "elapsed_ms": round((time.perf_counter() - exact_all_started) * 1000, 3), "candidate_count": size}
        total_ms = generation_ms + feature_ms + statistics.median(inference_runs) + exact_topk_ms
        results.append({"candidate_count": size, "top_k": min(TOP_K, size), "candidate_generation": {"elapsed_ms": round(generation_ms, 3), "throughput_per_second": round(1000 * size / max(generation_ms, 1e-9), 3)}, "feature_generation": {"elapsed_ms": round(feature_ms, 3), "throughput_per_second": round(1000 * size / max(feature_ms, 1e-9), 3)}, "ai_inference": median_summary(inference_runs), "ranking": {"elapsed_ms": round(statistics.median(inference_runs), 3), "supported_predictions": supported, "unsupported_predictions": size - supported}, "exact_top_k_verification": {"elapsed_ms": round(exact_topk_ms, 3), "verified_count": len(exact_results), "authoritative_result": True}, "exact_all": exact_all, "total_ai_plus_exact_top_k": {"elapsed_ms": round(total_ms, 3), "throughput_per_second": round(1000 * size / max(total_ms, 1e-9), 3)}, "peak_tracemalloc_mb": round(peak_mb, 3), "seed": 5, "model_version": bundle["metadata"]["model_bundle_version"]})
    artifact = {"schema_version": "goal6a-ai-scale-v1", "status": "PASS", "candidate_sizes": list(SIZES), "skipped_sizes": {"1000": "not measured: deterministic pre-solver feature extraction exceeded a practical release benchmark window; no extrapolation is reported"}, "results": results, "measurement_notes": ["All candidate and feature generation is actual deterministic CPU work.", "AI inference and exact top-K timings are actual measurements.", "Exact-all is measured only for N=20; it is explicitly skipped for larger N.", "Peak memory is tracemalloc Python allocation peak, not total OS RSS."], "exact_reference": "goal4b-exact-reference-v1"}
    output = ROOT / "artifacts/evals/performance/goal6a-ai-scale.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "sizes": artifact["candidate_sizes"], "totals_ms": {item["candidate_count"]: item["total_ai_plus_exact_top_k"]["elapsed_ms"] for item in results}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
