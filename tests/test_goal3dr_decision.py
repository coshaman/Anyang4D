from services.terrain.rescue_decision import decide_rescue


def test_rescue_decision_drops_street_level_path_when_no_candidate_reaches_b():
    decision = decide_rescue({"baseline": "TERRAIN_C", "contour": "TERRAIN_C", "rst": "METHOD_B_NOT_RUN", "tin": "METHOD_C_NOT_RUN"})
    assert decision["final_terrain_class"] == "TERRAIN_C"
    assert decision["STREET_LEVEL_FLOOD_TERRAIN_PATH"] == "DROP"
    assert decision["CITIZEN_HAZARD_ROUTING_FROM_TERRAIN"] == "DROP"
    assert decision["LEVEL_A_FLOOD_NEXT_GOAL_AUTHORIZED"] is False


def test_rescue_decision_keeps_citizen_gate_separate():
    decision = decide_rescue({"contour": "TERRAIN_A", "baseline": "TERRAIN_C"})
    assert decision["final_terrain_class"] == "TERRAIN_A"
    assert decision["LEVEL_A_FLOOD_NEXT_GOAL_AUTHORIZED"] is True
    assert decision["CITIZEN_ROAD_HAZARD_FUTURE_ELIGIBILITY"] is False
