from pathlib import Path

import pytest

from services.terrain.dxf import extract_constraints
from services.terrain.contracts import Bounds


def _write_fixture(path: Path) -> None:
    pairs = [
        ("0", "SECTION"), ("2", "ENTITIES"),
        ("0", "LWPOLYLINE"), ("5", "C1"), ("8", "F0017111"),
        ("38", "100.0"), ("90", "2"),
        ("10", "0"), ("20", "0"), ("10", "10"), ("20", "0"),
        ("0", "INSERT"), ("5", "P1"), ("8", "F0027217"),
        ("2", "ELEV"), ("10", "5"), ("20", "5"), ("30", "102.5"),
        ("0", "INSERT"), ("5", "X1"), ("8", "BUILDING"),
        ("2", "HOUSE"), ("10", "6"), ("20", "6"), ("30", "999"),
        ("0", "ENDSEC"), ("0", "EOF"),
    ]
    path.write_text("\n".join(value for pair in pairs for value in pair) + "\n", encoding="ascii")


def test_extracts_only_semantic_contours_and_spot_heights(tmp_path: Path):
    source = tmp_path / "37612048.dxf"
    _write_fixture(source)

    result = extract_constraints(source, "37612048", Bounds(0, 0, 10, 10))

    assert len(result.contours) == 1
    assert result.contours[0].elevation_m == 100.0
    assert result.contours[0].source_handle == "C1"
    assert len(result.spot_heights) == 1
    assert result.spot_heights[0].elevation_m == 102.5
    assert result.spot_heights[0].source_layer == "F0027217"
    assert result.rejected_entity_count == 1


def test_rejects_constraints_outside_bounds(tmp_path: Path):
    source = tmp_path / "37612048.dxf"
    _write_fixture(source)

    result = extract_constraints(source, "37612048", Bounds(20, 20, 30, 30))

    assert result.contours == []
    assert result.spot_heights == []


def test_invalid_sheet_number_is_rejected(tmp_path: Path):
    source = tmp_path / "37612048.dxf"
    _write_fixture(source)

    with pytest.raises(ValueError, match="sheet_number"):
        extract_constraints(source, "bad", Bounds(0, 0, 10, 10))
