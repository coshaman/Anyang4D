from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/evals/release/goal6a-release-audit.json"


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    required_docs = [
        "docs/COMPETITION_CLAIMS_MATRIX.md",
        "docs/COMPETITION_TECHNICAL_EVIDENCE.md",
        "docs/COMPETITION_ONE_PAGE.md",
        "docs/RELEASE_DATA_POLICY.md",
        "docs/GOAL6A_DECISION.md",
        "artifacts/evals/release/data-consistency.json",
        "artifacts/evals/release/ai-reproducibility.json",
        "artifacts/evals/performance/goal6a-ai-scale.json",
        "artifacts/evals/performance/goal6a-demo-runtime.json",
        "artifacts/evals/ui/goal6a-visual-review.md",
        "scripts/start_demo.ps1",
        "scripts/smoke_demo.ps1",
    ]
    claims = text("docs/COMPETITION_CLAIMS_MATRIX.md")
    policy = text("docs/RELEASE_DATA_POLICY.md")
    consistency = json.loads(text("artifacts/evals/release/data-consistency.json"))
    reproducibility = json.loads(text("artifacts/evals/release/ai-reproducibility.json"))
    scale = json.loads(text("artifacts/evals/performance/goal6a-ai-scale.json"))
    runtime = json.loads(text("artifacts/evals/performance/goal6a-demo-runtime.json"))
    checks = {
        "required_docs_and_artifacts": all((ROOT / path).exists() for path in required_docs),
        "data_consistency_pass": consistency.get("status") == "PASS" and all(consistency.get("checks", {}).values()),
        "ai_reproducibility_pass": reproducibility.get("status") == "PASS",
        "ai_scale_pass_and_1000_not_extrapolated": scale.get("status") == "PASS" and "1000" in scale.get("skipped_sizes", {}),
        "demo_runtime_pass_and_real_browser": runtime.get("status") == "PASS" and runtime.get("timings", {}).get("measurement_mode") == "real browser, real backend, no mocked core requests",
        "claims_matrix_has_forbidden_boundaries": all(term in claims for term in ["AI disaster prediction", "flood prediction", "predicted flood depth", "safe route", "real-time population", "actual citizen locations", "official emergency forecast", "AI-verified safety"]),
        "release_policy_has_ngii_and_osm_rules": "Raw NGII DXF and DEM" in policy and "ODbL" in policy and "BSD-3-Clause" in policy,
        "gitignore_has_secret_and_cache_guards": all(term in text(".gitignore") for term in [".env", ".venv/", "test-results/"]),
        "public_docs_have_no_machine_absolute_paths": not any("C:\\Users\\" in text(path) for path in required_docs if (ROOT / path).suffix in {".md", ".json"}),
        "frozen_boundary_is_documented": all(term in claims for term in ["TERRAIN_C", "DROP", "AI_SURROGATE_B", "DEMO_ONLY"]),
    }
    payload = {"schema_version": "goal6a-release-audit-v1", "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "release_classification": "COMPETITION_RELEASE_B"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
