from __future__ import annotations

import json
from pathlib import Path

from services.ai_surrogate.dataset import DEFAULT_DIR, load_rows
from services.ai_surrogate.model import train_bundle


def main() -> None:
    metadata = train_bundle(load_rows(), Path("models/scenario_triage"))
    print(json.dumps({"model_name": metadata["model_name"], "bundle": "models/scenario_triage/model.joblib", "validation": metadata["evaluation"]["selected_model_validation"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
