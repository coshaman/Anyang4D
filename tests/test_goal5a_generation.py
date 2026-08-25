from services.ai_surrogate.features import extract_features
from services.ai_surrogate.scenarios import generate_candidates


def test_goal5a_scenario_generation_is_deterministic_and_unique():
    first = [scenario.to_dict() for scenario in generate_candidates(seed=17, count=16)]
    second = [scenario.to_dict() for scenario in generate_candidates(seed=17, count=16)]
    assert first == second
    assert len({scenario["scenario_id"] for scenario in first}) == 16
    assert {scenario["provenance"] for scenario in first} == {"SIMULATED_ADMIN_SCENARIO"}


def test_goal5a_features_are_pre_solver_and_numeric():
    scenario = generate_candidates(seed=19, count=1)[0]
    features = extract_features(scenario)
    assert features["affected_population"] >= 0
    assert features["evacuation_demand"] >= 0
    assert all(isinstance(value, float) for value in features.values())
    assert not any(name in features for name in {"assigned", "unserved", "average_assigned_travel_distance_m", "facility_load"})
