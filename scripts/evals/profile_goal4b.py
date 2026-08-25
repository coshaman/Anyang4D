from __future__ import annotations

import cProfile
import json
import pstats
import statistics
import time
from io import StringIO
from pathlib import Path

from services.api.goal4a import STORE, _ensure_presets, _facilities, _graph, _resource_payload
from services.simulator.contracts import Scenario
from services.simulator.engine import derive_evacuation_demand, resolve_frame, solve_assignment

ROOT = Path(__file__).resolve().parents[2]
_ensure_presets()
scenario = STORE.get("anyang-flood-style-admin")
graph, coords = _graph()
facilities = _facilities()
resources = _resource_payload()
roads = [{"edge_id": data.get("edge_id", f"{first}-{second}"), "a": (coords[first][1], coords[first][0]), "b": (coords[second][1], coords[second][0])} for first, second, data in graph.edges(data=True)]

parse_samples: list[float] = []
geometry_samples: list[float] = []
assignment_samples: list[float] = []
serialization_samples: list[float] = []
subsystems: list[dict[str, float]] = []
for _ in range(3):
    encoded = json.dumps(scenario.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    started = time.perf_counter()
    parsed = Scenario.from_dict(json.loads(encoded))
    parse_samples.append((time.perf_counter() - started) * 1000)
    started = time.perf_counter()
    frame = resolve_frame(parsed, 20, roads, facilities, resources)
    geometry_samples.append((time.perf_counter() - started) * 1000)
    units, demand_meta = derive_evacuation_demand(frame, parsed, parsed.demand_units)
    timing: dict[str, float] = {}
    started = time.perf_counter()
    assignment = solve_assignment(frame, parsed, units, facilities, graph, coords, timing=timing)
    assignment_samples.append((time.perf_counter() - started) * 1000)
    started = time.perf_counter()
    json.dumps({"frame": frame.__dict__, "assignment": assignment, "demand": demand_meta}, default=lambda value: value.__dict__, ensure_ascii=False)
    serialization_samples.append((time.perf_counter() - started) * 1000)
    subsystems.append(timing)

profile = cProfile.Profile()
profile.enable()
solve_assignment(frame, parsed, units, facilities, graph, coords)
profile.disable()
stream = StringIO()
pstats.Stats(profile, stream=stream).sort_stats("cumulative").print_stats(20)
artifact = {
    "scenario_id": scenario.scenario_id,
    "frame": 20,
    "graph_nodes": graph.number_of_nodes(),
    "graph_edges": graph.number_of_edges(),
    "demand_units": len(scenario.demand_units),
    "facility_count": len(facilities),
    "samples": 3,
    "median_ms": {
        "scenario_parsing": round(statistics.median(parse_samples), 3),
        "geometry_and_hazard_road_intersection": round(statistics.median(geometry_samples), 3),
        "assignment_total": round(statistics.median(assignment_samples), 3),
        "serialization": round(statistics.median(serialization_samples), 3),
    },
    "assignment_subsystems_median_ms": {key: round(statistics.median(item.get(key, 0) for item in subsystems), 3) for key in subsystems[0]},
    "profiler_top20_cumulative": stream.getvalue(),
    "method": "instrumented deterministic Goal 4A solver; same bounded demo AOI",
}
out = ROOT / "artifacts/evals/performance/goal4b-profile-before.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(out), "median_ms": artifact["median_ms"], "assignment_subsystems_median_ms": artifact["assignment_subsystems_median_ms"]}, ensure_ascii=False))
