"""Bounded Goal 4A runtime benchmark for the interactive demo AOI."""
from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from services.api.goal4a import STORE, _ensure_presets, _frame_payload

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/evals/performance/goal4a-runtime.json"


def main() -> None:
    _ensure_presets()
    scenario = STORE.get("anyang-flood-style-admin")
    timings = []
    for minute in scenario.frame_times():
        started = time.perf_counter()
        frame = _frame_payload(scenario, minute)
        timings.append({"time_minute": minute, "elapsed_ms": round((time.perf_counter() - started) * 1000, 2), "changed_roads": frame["roads"]["changed_count"], "assigned": frame["assignment"]["assigned"], "unserved": frame["assignment"]["unserved"]})
    payload = {"scenario_id": scenario.scenario_id, "graph": "bounded OSM demo snapshot", "demand_units": len(scenario.demand_units), "total_demand": sum(unit.population for unit in scenario.demand_units), "frames": timings, "median_ms": round(statistics.median(item["elapsed_ms"] for item in timings), 2), "max_ms": round(max(item["elapsed_ms"] for item in timings), 2), "method": "cached road geometry + demand-origin single-source Dijkstra + deterministic min-cost flow", "interpretation": "benchmark evidence for the bounded administrative demo AOI; not a whole-city real-time SLA"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
