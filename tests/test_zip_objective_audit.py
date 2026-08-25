from pathlib import Path

from services.release.zip_audit import build_zip_objective_audit


def test_zip_objective_audit_separates_implemented_work_from_external_gates():
    audit = build_zip_objective_audit(Path(__file__).resolve().parents[1])
    assert audit["status"] == "FINAL_PRODUCT_READY_PENDING_HUMAN_ACTIONS"
    assert audit["implemented"]["goal_0_foundation"] is True
    assert audit["implemented"]["goal_1_data_audit"] is True
    assert audit["implemented"]["goal_2_real_data_citizen_ui"] is True
    assert audit["implemented"]["goal_3_flood_gate_documented"] is True
    assert audit["implemented"]["goal_5_capacity_admin_engine"] is True
    assert audit["implemented"]["goal_7_optional_modules_decided"] is True
    assert audit["closed_research_branches"]["native_2020_plus_1m_or_5m_dem"] is False
    assert audit["release_gates"]["terrain_dependency_for_release"] is True
    assert audit["release_gates"]["terrain_rainfall_dependency_closed"] is True
    assert audit["remaining"] == []
