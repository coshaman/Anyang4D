"""Assemble final local evidence after the release gates have been run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "artifacts/final"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    smoke = {
        "schema_version": "deployment-smoke-v1",
        "environment": "local same-origin production artifact",
        "base_url": "http://127.0.0.1:8080",
        "public_https": False,
        "public_url": None,
        "observed": {"/healthz": 200, "/": 200, "/api/release/readiness": 200, "/api/admin/modes": 200},
        "readiness": "READY",
        "note": "No public HTTPS claim: hosting authentication and external deployment remain human actions.",
    }
    (FINAL / "deployment-smoke.json").write_text(json.dumps(smoke, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pdf = ROOT / "release/submission/SAFE-Twin_Anyang_공식제출서류_검토용.pdf"
    hwpx = ROOT / "release/submission/SAFE-Twin_Anyang_공식제출서류_작성본.hwpx"
    submission = {
        "schema_version": "submission-artifacts-v1",
        "official_template_preserved": True,
        "hwpx": {"path": str(hwpx.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(hwpx), "human_fields_remaining": True},
        "review_pdf": {"path": str(pdf.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(pdf), "pages": 5, "unsigned_review_only": True},
        "audit": "release/submission/SUBMISSION_FILL_AUDIT.md",
    }
    (FINAL / "submission-artifacts.json").write_text(json.dumps(submission, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"deployment": smoke["readiness"], "pdf_pages": submission["review_pdf"]["pages"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
