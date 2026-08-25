from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from services.release.zip_audit import build_zip_objective_audit


OUTPUT = ROOT / "artifacts/evals/release/zip-objective-audit.json"


if __name__ == "__main__":
    payload = build_zip_objective_audit(ROOT)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
