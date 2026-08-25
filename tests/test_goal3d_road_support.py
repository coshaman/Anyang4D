from services.terrain.road_support import nearest_constraint_distance


def test_nearest_constraint_distance():
    assert nearest_constraint_distance([(0.0, 0.0), (10.0, 0.0)], (3.0, 4.0)) == 5.0
