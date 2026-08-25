from services.flood.dem_quality import assess_dem_quality, detect_duplicate_sources


def test_goal3c_rejects_calling_a_90m_dem_a_5m_dem():
    result = assess_dem_quality(
        {
            "width": 254,
            "height": 316,
            "res": [90.0, 90.0],
            "crs": "EPSG:5179",
            "nodata": -9999.0,
            "driver": "HFA",
        }
    )

    assert result.native_resolution_m == 90.0
    assert result.is_native_1m is False
    assert result.is_native_5m is False
    assert result.display_grid_resolution_m == 5.0
    assert result.display_grid_is_derived is True
    assert result.goal3c_real_terrain_gate is False


def test_goal3c_detects_byte_identical_uploaded_sources():
    result = detect_duplicate_sources(
        [
            {"name": "37612049.zip", "sha256": "same"},
            {"name": "37612058.zip", "sha256": "same"},
        ]
    )

    assert result.duplicate_count == 1
    assert result.unique_source_count == 1
    assert result.is_duplicate_upload is True
