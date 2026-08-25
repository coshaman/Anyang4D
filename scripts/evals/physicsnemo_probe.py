"""Small, non-product PhysicsNeMo environment probe.

The probe intentionally fails closed: it never labels a NumPy fallback as
PhysicsNeMo. Run it in an isolated environment after installing the approved
PhysicsNeMo package and PyTorch.
"""

from __future__ import annotations

import importlib.util
import json
import platform
from pathlib import Path


def main() -> int:
    torch_available = importlib.util.find_spec("torch") is not None
    physicsnemo_available = importlib.util.find_spec("physicsnemo") is not None
    result = {
        "experiment": "physicsnemo_swe_minimal",
        "provenance": "SYNTHETIC",
        "product_integration": False,
        "platform": platform.platform(),
        "torch_available": torch_available,
        "physicsnemo_available": physicsnemo_available,
        "status": "READY_TO_RUN" if torch_available and physicsnemo_available else "BLOCKED_ENVIRONMENT",
        "reason": None
        if torch_available and physicsnemo_available
        else "PyTorch and/or PhysicsNeMo is not installed in the project environment; no flood result was produced.",
        "expected_check": "one forward/loss step on a synthetic shallow-water tensor with finite loss",
    }
    output = Path("artifacts/evals/ml/physicsnemo/physicsnemo_probe.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
