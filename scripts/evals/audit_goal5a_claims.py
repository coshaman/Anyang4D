from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = ["AI 재난 예측", "실제 피해 예측", "AI 안전 경로", "침수 확률", "OBSERVED_DAMAGE", "REAL_DISASTER_PROBABILITY", "OFFICIAL_FORECAST"]
SCOPE = [ROOT / "services/ai_surrogate", ROOT / "services/api/goal5a.py", ROOT / "apps/web/src/AdminSimulator.tsx", ROOT / "apps/web/src/App.tsx"]


def main() -> None:
    violations = []
    for target in SCOPE:
        paths = [target] if target.is_file() else list(target.rglob("*"))
        for path in paths:
            if path.suffix not in {".py", ".tsx", ".ts"}:
                continue
            text = path.read_text(encoding="utf-8")
            for term in FORBIDDEN:
                if term in text:
                    violations.append(f"{path}:{term}")
    if violations:
        raise SystemExit("unsupported Goal5A claim(s): " + ", ".join(violations))
    print("goal5a claim audit passed")


if __name__ == "__main__":
    main()
