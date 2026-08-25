from pathlib import Path

from services.terrain.contracts import ConstraintSet, ElevationConstraint
from services.terrain.topology import audit_contour_topology


def test_contour_topology_reports_intervals_closed_duplicates_and_dangling():
    first = ElevationConstraint("a", "F0017111", "1", "contour", 100.0, ((0, 0), (10, 0)))
    duplicate = ElevationConstraint("a", "F0017111", "2", "contour", 100.0, ((0, 0), (10, 0)))
    closed = ElevationConstraint("a", "F0017111", "3", "contour", 105.0, ((0, 5), (10, 5), (0, 5)))
    result = audit_contour_topology([ConstraintSet(Path("a"), "h", "a", [first, duplicate, closed], [])])

    assert result["unique_elevations_m"] == [100.0, 105.0]
    assert result["interval_distribution_m"]["5.0"] == 1
    assert result["closed_contour_count"] == 1
    assert result["duplicate_geometry_count"] == 1
    assert result["dangling_endpoint_count"] >= 2


def test_contour_topology_detects_crossing_lines():
    a = ElevationConstraint("a", "F0017111", "1", "contour", 100.0, ((0, 0), (10, 10)))
    b = ElevationConstraint("a", "F0017111", "2", "contour", 105.0, ((0, 10), (10, 0)))
    result = audit_contour_topology([ConstraintSet(Path("a"), "h", "a", [a, b], [])])
    assert result["crossing_pair_count"] == 1
