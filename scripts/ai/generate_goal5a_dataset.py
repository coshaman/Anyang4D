from __future__ import annotations

import argparse
import json

from services.ai_surrogate.dataset import generate_labels
from services.ai_surrogate.scenarios import generate_candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=5)
    parser.add_argument("--count", type=int, default=160)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate_labels(generate_candidates(args.seed, args.count), resume=not args.no_resume), ensure_ascii=False))


if __name__ == "__main__":
    main()
