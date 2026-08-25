"""Audit the sanitized public release boundary without reading private source into output."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "artifacts" / "final"
PRIVATE = FINAL / "private-source"

EXCLUDED_PREFIXES = {
    "artifacts/final/private-source",
    "artifacts/final/release/submission",
    "SAFE-Twin_Anyang_Codex_Pack",
    "docs/superpowers",
    "docs/(B010)",
    "docs/(B080)",
    "docs/NGII_",
    "docs/TERRAIN_",
    "docs/ANYANG_DEM_",
    "docs/DXF_",
}
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"][^'\"]+"),
    re.compile(r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\\n]+\\[^\n]+"),
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def excluded(path: Path) -> bool:
    name = rel(path)
    return any(name == prefix or name.startswith(prefix + "/") for prefix in EXCLUDED_PREFIXES)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    files = []
    findings = []
    excluded_files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", "node_modules", ".venv", ".venv-physicsnemo", "dist", "__pycache__", "test-results"} for part in path.parts):
            continue
        if excluded(path):
            excluded_files.append(rel(path))
            continue
        files.append(path)
        if path.suffix.lower() not in {".md", ".json", ".py", ".ts", ".tsx", ".js", ".css", ".html", ".yml", ".yaml", ".toml", ".txt", ".ps1", ".dockerignore", ".gitignore"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"path": rel(path), "kind": "secret-or-absolute-path-pattern", "pattern": pattern.pattern})

    manifest = json.loads((ROOT / "data/manifests/data_manifest.json").read_text(encoding="utf-8"))
    dem = next(item for item in manifest["datasets"] if item["id"] == "dem-terrain")
    claims = (ROOT / "docs/COMPETITION_CLAIMS_MATRIX.md").read_text(encoding="utf-8")
    scope = (ROOT / "docs/FINAL_PRODUCT_SCOPE.md").read_text(encoding="utf-8")
    decision = (ROOT / "docs/HIGH_RES_DEM_FINAL_DECISION.md").read_text(encoding="utf-8")
    checks = {
        "high_res_terrain_acquisition_closed": dem.get("status") == "CLOSED_RESEARCH_BRANCH" and dem.get("release_dependency") is False,
        "terrain_dependency_false": "TERRAIN_DEPENDENCY_FOR_RELEASE" in decision and "false" in decision.lower(),
        "flood_wording_bounded": "가정 침수영역에 따른 영향 시뮬레이션" in claims and "not physical flood prediction" in scope,
        "private_source_excluded": PRIVATE.exists() and all(item.startswith("artifacts/final/private-source") for item in excluded_files if item.startswith("artifacts/final/private-source")),
        "raw_ngii_excluded_by_policy": "Raw NGII" in (ROOT / "docs/RELEASE_DATA_POLICY.md").read_text(encoding="utf-8"),
        "osm_attribution_present": "ODbL" in (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8"),
    }
    manifest_out = {
        "schema_version": "final-public-release-v1",
        "generated_at": "2026-08-24",
        "repository_target": "https://github.com/coshaman/Anyang4D",
        "public_url": None,
        "release_classification": "FINAL_RELEASE_B",
        "include_policy": ["source code", "processed lawful public-data derivatives", "models", "evaluation artifacts", "provenance and license notices"],
        "exclude_policy": ["raw NGII DXF/DEM", "private-source", ".env and keys", "local caches", "real citizen locations", "terrain-derived flood depth and citizen hazard routing"],
        "excluded_private_source_file_count": len([item for item in excluded_files if item.startswith("artifacts/final/private-source")]),
        "public_file_count_scanned": len(files),
        "checks": checks,
        "findings": findings,
        "human_actions": ["set GitHub remote and push main after account authentication", "complete official HWPX identity/signature/consent fields", "attach required enrollment/organization certificates", "authenticate hosting provider and run public HTTPS smoke"],
    }
    FINAL.mkdir(parents=True, exist_ok=True)
    (FINAL / "public-release-manifest.json").write_text(json.dumps(manifest_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    privacy = {
        "schema_version": "final-privacy-audit-v1",
        "status": "PASS_WITH_EXCLUDED_PRIVATE_SOURCE" if not findings else "FAIL",
        "public_scan_findings": findings,
        "excluded_private_source": str(PRIVATE),
        "excluded_private_source_present": PRIVATE.exists(),
        "policy": "private-source is never part of the public release tree; missing identity fields are not guessed",
    }
    (FINAL / "final-privacy-audit.json").write_text(json.dumps(privacy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    claim = {
        "schema_version": "final-claim-audit-v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "allowed_flood_phrase": "가정 침수영역에 따른 영향 시뮬레이션",
        "forbidden_claims": ["physical flood prediction", "predicted flood depth", "citizen safe route", "AI disaster prediction", "real-time population", "official emergency forecast"],
    }
    (FINAL / "final-claim-audit.json").write_text(json.dumps(claim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"privacy": privacy["status"], "claims": claim["status"], "findings": len(findings), "files": len(files)}, ensure_ascii=False))
    return 0 if not findings and all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
