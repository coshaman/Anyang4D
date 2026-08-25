from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {".ts", ".tsx", ".css", ".html"}
SOURCE_ROOTS = ("apps", "packages", "services")
FORBIDDEN = [
    r"AI 기반",
    r"AI-powered",
    r"스마트 인사이트",
    r"backdrop-filter",
    r"glassmorphism",
    r"sparkle",
    r"robot",
    r"brain icon",
]


def main() -> int:
    violations: list[str] = []
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or path.suffix not in EXTENSIONS
            or "node_modules" in path.parts
            or (path.parts and path.parts[0] not in SOURCE_ROOTS and path.name != "index.html")
        ):
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"{path.relative_to(ROOT)}: {pattern}")
    if violations:
        print("anti-slop violations:")
        print("\n".join(violations))
        return 1
    print("anti-slop check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
