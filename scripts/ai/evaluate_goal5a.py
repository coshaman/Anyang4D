from __future__ import annotations

import json
from pathlib import Path

from services.ai_surrogate.dataset import DEFAULT_DIR, load_rows
from services.ai_surrogate.evaluate import evaluate_models, write_evaluation


def main() -> None:
    artifact = evaluate_models(load_rows())
    write_evaluation(artifact, Path("artifacts/evals/ai/goal5a/evaluation.json"))
    print(json.dumps(artifact["results"], ensure_ascii=False))


if __name__ == "__main__":
    main()
