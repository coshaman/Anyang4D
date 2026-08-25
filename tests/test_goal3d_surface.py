from pathlib import Path

import numpy as np

from services.terrain.contracts import Bounds, ConstraintSet, ElevationConstraint
from services.terrain.interpolation import IDWSurface, build_surface
from services.terrain.support import summarize_support


def _constraints() -> ConstraintSet:
    contours = [
        ElevationConstraint("37612048", "F0017111", "c1", "contour", 100, ((0, 0), (10, 0))),
        ElevationConstraint("37612048", "F0017111", "c2", "contour", 110, ((0, 10), (10, 10))),
    ]
    spots = [ElevationConstraint("37612048", "F0027217", "p1", "spot_height", 105, ((5, 5),))]
    return ConstraintSet(Path("fixture.dxf"), "hash", "37612048", contours, spots)


def test_idw_surface_is_deterministic_and_finite():
    result = build_surface(_constraints(), Bounds(0, 0, 10, 10), 5, method="idw")
    again = build_surface(_constraints(), Bounds(0, 0, 10, 10), 5, method="idw")
    assert isinstance(result, IDWSurface)
    assert np.array_equal(result.elevation, again.elevation)
    assert np.isfinite(result.elevation).all()
    assert 100 <= result.elevation[0, 0] <= 110


def test_support_reports_counts_and_density():
    summary = summarize_support(_constraints(), Bounds(0, 0, 10, 10))
    assert summary["contour_count"] == 2
    assert summary["spot_height_count"] == 1
    assert summary["valid_constraint_count"] == 3
    assert summary["contour_length_m"] == 20.0
