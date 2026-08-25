import json
from pathlib import Path

import pytest

from services.terrain.loader import validate_terrain_metadata


def test_loader_rejects_flood_authorization(tmp_path: Path):
    metadata = tmp_path / "quality.json"
    metadata.write_text(json.dumps({"provenance": "DERIVED_TERRAIN_FROM_TOPOGRAPHIC_VECTORS", "source_crs": "EPSG:5186", "authorization": {"flood_simulation": True}}), encoding="utf-8")
    with pytest.raises(ValueError, match="flood"):
        validate_terrain_metadata(metadata)


def test_loader_accepts_terrain_only_metadata(tmp_path: Path):
    metadata = tmp_path / "quality.json"
    metadata.write_text(json.dumps({"provenance": "DERIVED_TERRAIN_FROM_TOPOGRAPHIC_VECTORS", "source_crs": "EPSG:5186", "authorization": {"flood_simulation": False}}), encoding="utf-8")
    assert validate_terrain_metadata(metadata)["source_crs"] == "EPSG:5186"
