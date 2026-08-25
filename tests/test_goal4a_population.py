from services.simulator.data import load_population_demand, load_simulation_facilities
from services.simulator.presets import build_presets


def test_official_population_demand_is_exact_and_explicitly_allocated():
    units = load_population_demand()
    assert len(units) == 31
    assert sum(unit["population"] for unit in units) == 562143
    assert {unit["provenance"] for unit in units} == {"OFFICIAL"}
    assert {unit["allocation_method"] for unit in units} == {"SIMULATED_SPATIAL_ALLOCATION_UNIFORM_DONG_ANCHOR"}


def test_all_presets_use_official_population_total():
    units = load_population_demand()
    for scenario in build_presets(load_simulation_facilities(), units):
        assert sum(unit.population for unit in scenario.demand_units) == sum(unit["population"] for unit in units)
        assert {unit.provenance for unit in scenario.demand_units} == {"OFFICIAL"}
