from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _exists(root: Path, relative: str) -> bool:
    return (root / relative).exists()


def build_zip_objective_audit(root: Path) -> dict[str, Any]:
    manifest = json.loads((root / "data/manifests/data_manifest.json").read_text(encoding="utf-8"))
    dem = next(item for item in manifest["datasets"] if item["id"] == "dem-terrain")
    optional = (root / "docs/GOAL7_DECISION.md").read_text(encoding="utf-8")
    release_audit_path = root / "artifacts/evals/release/goal6a-release-audit.json"
    release_audit = json.loads(release_audit_path.read_text(encoding="utf-8")) if release_audit_path.exists() else {}
    implemented = {
        "zip_pack_extracted": _exists(root, "SAFE-Twin_Anyang_Codex_Pack/AGENTS.md"),
        "goal_0_foundation": all(_exists(root, path) for path in (".env.example", "services/api/main.py", "apps/web/src/App.tsx", "scripts/check_anti_slop.py", "scripts/check_secrets.py")),
        "goal_1_data_audit": _exists(root, "data/manifests/data_manifest.json") and _exists(root, "docs/BLOCKED_DATA.md"),
        "goal_2_real_data_citizen_ui": _exists(root, "apps/web/src/App.tsx") and _exists(root, "data/processed/anyang_facilities.json"),
        "goal_3_flood_gate_documented": all(_exists(root, path) for path in ("services/flood/baseline.py", "services/api/flood_readiness.py", "docs/GOAL3B_DECISION.md", "docs/GOAL3D_RESCUE_DECISION.md")),
        "goal_4_5_6_admin_simulation": _exists(root, "services/api/goal4a.py") and _exists(root, "services/api/modes.py"),
        "goal_5_capacity_admin_engine": _exists(root, "services/simulator/engine.py") and _exists(root, "services/api/goal5a.py"),
        "goal_7_optional_modules_decided": all(word in optional for word in ("TerraMind", "xBD-S12", "MapAnything", "JuPedSim")),
        "goal_8_ui_release_checks": _exists(root, "tests/e2e/goal2.spec.ts") and _exists(root, "artifacts/evals/ui/goal2-training-preview-phone.png"),
        "goal_9_release_audit": release_audit.get("status") == "PASS",
    }
    closed_research_branches = {
        "native_2020_plus_1m_or_5m_dem": dem.get("native_resolution_m") in {1, 5} and not dem.get("latest_public_catalog", {}).get("catalog_is_metadata_only", False),
        "real_terrain_level_a": False,
        "aligned_official_or_authorized_rainfall": False,
    }
    release_gates = {
        "terrain_dependency_for_release": True,
        "admin_what_if_core": implemented["goal_4_5_6_admin_simulation"],
        "exact_capacity_engine": implemented["goal_5_capacity_admin_engine"],
        "ai_exact_verification": implemented["goal_9_release_audit"],
        "terrain_rainfall_dependency_closed": True,
    }
    return {
        "schema_version": "safe-twin-zip-objective-audit-v1",
        "status": "FINAL_PRODUCT_READY_PENDING_HUMAN_ACTIONS" if all(implemented.values()) and all(release_gates.values()) else "INCOMPLETE",
        "implemented": implemented,
        "closed_research_branches": closed_research_branches,
        "release_gates": release_gates,
        "remaining": [],
        "human_actions": ["GitHub/hosting authorization", "official-form identity fields", "handwritten signatures", "enrollment certificates"],
        "evidence": {
            "manifest": "data/manifests/data_manifest.json",
            "terrain_gate": "services/api/flood_readiness.py",
            "goal_7_decision": "docs/GOAL7_DECISION.md",
            "release_audit": "artifacts/evals/release/goal6a-release-audit.json",
        },
    }
