from pathlib import Path

from services.flood.pipeline import run_synthetic_evaluation


if __name__ == "__main__":
    print(run_synthetic_evaluation(Path("artifacts/evals/ml/goal3b")))
