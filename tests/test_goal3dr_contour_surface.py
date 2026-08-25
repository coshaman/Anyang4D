from pathlib import Path

import numpy as np

from services.terrain.contracts import Bounds, ConstraintSet, ElevationConstraint
from services.terrain.rescue import build_contour_aware_surface, predict_contour_aware


def test_contour_aware_surface_interpolates_between_isolines():
    constraints = ConstraintSet(
        Path("fixture"), "hash", "x",
        [
            ElevationConstraint("x", "F0017111", "low", "contour", 100.0, ((0, 0), (10, 0))),
            ElevationConstraint("x", "F0017111", "high", "contour", 110.0, ((0, 10), (10, 10))),
        ], [],
    )
    surface = build_contour_aware_surface(constraints, Bounds(0, 0, 10, 10), 5.0)

    assert surface.method == "contour_aware_distance"
    assert np.isclose(surface.elevation[1, 1], 105.0)
    assert np.isfinite(surface.elevation).all()


def test_contour_aware_prediction_uses_isoline_distance():
    constraints = ConstraintSet(
        Path("fixture"), "hash", "x",
        [
            ElevationConstraint("x", "F0017111", "low", "contour", 100.0, ((0, 0), (10, 0))),
            ElevationConstraint("x", "F0017111", "high", "contour", 110.0, ((0, 10), (10, 10))),
        ], [],
    )
    assert np.isclose(predict_contour_aware(constraints, [(5, 5)])[0], 105.0)
