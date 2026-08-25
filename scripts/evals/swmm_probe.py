"""Record whether a real SWMM executable/wrapper is available; no city model is built."""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


def main() -> int:
    executable = shutil.which("swmm5") or shutil.which("swmm5.exe") or shutil.which("swmm")
    wrapper = importlib.util.find_spec("pyswmm") is not None
    report = {
        "experiment": "swmm_environment_probe",
        "provenance": "SYNTHETIC",
        "product_integration": False,
        "swmm_executable": executable,
        "pyswmm_available": wrapper,
        "status": "READY_TO_RUN" if executable else "BLOCKED_ENVIRONMENT",
        "reason": None if executable else "No SWMM executable is installed; no Anyang .inp was fabricated.",
        "required_city_inputs": [
            "rainfall time series",
            "subcatchments and imperviousness/infiltration",
            "nodes, links, outfalls and boundary conditions",
            "conduit geometry/inverts/roughness",
            "calibration observations",
        ],
    }
    output = Path("artifacts/evals/ml/swmm/swmm_probe.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
