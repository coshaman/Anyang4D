from services.api.goal4a import _frame_payload
from services.simulator.contracts import Scenario
from services.simulator.data import load_population_demand
from services.simulator.presets import build_presets
from services.simulator.data import load_simulation_facilities


def test_exact_frame_exposes_aggregated_evacuation_flow_coordinates():
    demand = load_population_demand()
    scenario = next(item for item in build_presets(load_simulation_facilities(), demand) if item.scenario_id == "anyang-general-evacuation-competition")
    payload = _frame_payload(scenario, scenario.frame_times()[0])
    assert payload["evacuation_flow"]
    flow = payload["evacuation_flow"][0]
    assert set(flow) >= {"demand_node_id", "shelter_id", "assigned_demand", "load_ratio", "geometry"}
    assert flow["assigned_demand"] > 0
    assert flow["geometry"]["type"] == "LineString"


def test_v2_demo_preset_has_four_distinct_visual_states():
    scenarios = build_presets(load_simulation_facilities(), load_population_demand())
    demo = next(item for item in scenarios if item.scenario_id == "anyang-v2-four-state-demo")
    assert demo.frame_times() == [0, 10, 20, 30]
    assert len({repr(item.geometry) for item in demo.hazard_keyframes}) == 4
