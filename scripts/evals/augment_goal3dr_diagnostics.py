from __future__ import annotations

import json
from pathlib import Path

import rasterio

from services.terrain.validation import terrain_diagnostics


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "artifacts/evals/terrain/goal3dr/contour/quality.json"
COMPARISON = ROOT / "artifacts/evals/terrain/goal3dr/method-comparison.json"
RASTER = ROOT / "artifacts/evals/terrain/goal3dr/contour/terrain.tif"


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    with rasterio.open(RASTER) as dataset:
        values = dataset.read(1)
        spacing = float(abs(dataset.transform.a))
    diagnostics = terrain_diagnostics(values, spacing)
    report["diagnostics"] = diagnostics
    report["slope_p99"] = diagnostics["slope_p99"]
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    comparison = json.loads(COMPARISON.read_text(encoding="utf-8"))
    holdout = comparison["holdout_identity"]
    holdout["spot_sample_ids"] = [f"{value}#{index}" for index, value in enumerate(holdout.get("spot_ids", []))]
    holdout["contour_sample_ids"] = [f"{value}#{index}" for index, value in enumerate(holdout.get("contour_ids", []))]
    topology_path = ROOT / "artifacts/evals/terrain/goal3dr/contour-topology.json"
    topology = json.loads(topology_path.read_text(encoding="utf-8"))
    topology["holdout"]["spot_sample_ids"] = holdout["spot_sample_ids"]
    topology["holdout"]["contour_sample_ids"] = holdout["contour_sample_ids"]
    topology_path.write_text(json.dumps(topology, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for method in comparison["methods"]:
        if method["method"] == "contour_aware_distance":
            method["sink_cell_count"] = diagnostics["sink_cell_count"]
            method["flow_direction_counts"] = diagnostics["flow_direction_counts"]
            method["flow_accumulation_max"] = diagnostics["flow_accumulation_max"]
    COMPARISON.write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
