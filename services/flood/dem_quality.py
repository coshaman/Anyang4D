"""Evidence-based quality gates for supplied NGII DEM rasters."""

from dataclasses import dataclass
from math import isclose
from typing import Iterable, Mapping


@dataclass(frozen=True)
class DemQuality:
    native_resolution_m: float
    is_native_1m: bool
    is_native_5m: bool
    display_grid_resolution_m: float
    display_grid_is_derived: bool
    goal3c_real_terrain_gate: bool


@dataclass(frozen=True)
class DuplicateSourceReport:
    duplicate_count: int
    unique_source_count: int
    is_duplicate_upload: bool


def assess_dem_quality(metadata: Mapping[str, object], *, display_resolution_m: float = 5.0) -> DemQuality:
    """Classify native spacing without promoting an interpolated grid to DEM truth."""
    res = metadata.get("res")
    if not isinstance(res, (list, tuple)) or len(res) != 2:
        raise ValueError("DEM metadata must contain two resolution values")
    x_res, y_res = (abs(float(res[0])), abs(float(res[1])))
    if x_res <= 0 or y_res <= 0 or not isclose(x_res, y_res, rel_tol=0, abs_tol=1e-6):
        raise ValueError("DEM raster must have a positive square cell size")
    native = x_res
    native_1m = isclose(native, 1.0, rel_tol=0, abs_tol=1e-6)
    native_5m = isclose(native, 5.0, rel_tol=0, abs_tol=1e-6)
    return DemQuality(
        native_resolution_m=native,
        is_native_1m=native_1m,
        is_native_5m=native_5m,
        display_grid_resolution_m=float(display_resolution_m),
        display_grid_is_derived=not isclose(native, float(display_resolution_m), rel_tol=0, abs_tol=1e-6),
        # Goal 3C requires a defensible high-resolution source, not just interpolation.
        goal3c_real_terrain_gate=native_1m or native_5m,
    )


def detect_duplicate_sources(sources: Iterable[Mapping[str, str]]) -> DuplicateSourceReport:
    hashes = [str(source.get("sha256", "")).lower() for source in sources]
    nonempty = [value for value in hashes if value]
    unique = set(nonempty)
    return DuplicateSourceReport(
        duplicate_count=len(nonempty) - len(unique),
        unique_source_count=len(unique),
        is_duplicate_upload=bool(nonempty) and len(unique) == 1 and len(nonempty) > 1,
    )
