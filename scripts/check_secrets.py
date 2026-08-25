from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"(?:api[_-]?key|service[_-]?key|secret)\s*[=:]\s*[\"'][^\"']{12,}[\"']",
]
IGNORED = {"package-lock.json", "check_secrets.py"}
IGNORED_DIRS = {"node_modules", ".venv", ".venv-physicsnemo", "dist", "test-results", "artifacts", ".git"}


def main() -> int:
    violations: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name in IGNORED or IGNORED_DIRS.intersection(path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(str(path.relative_to(ROOT)))
                break
    if violations:
        print("possible secrets found:\n" + "\n".join(violations))
        return 1
    print("secret check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
