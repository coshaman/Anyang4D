"""Goal 3A decision helpers for flood-model evidence and provenance."""

from __future__ import annotations

from typing import Any


LICENSE_STATUSES = {"GO", "CONDITIONAL", "HOLD", "DROP"}
PROVENANCE = {"SYNTHETIC", "BENCHMARK", "ANYANG_OFFICIAL", "FUTURE_ANYANG"}


def license_record(name: str, license_name: str, status: str, evidence_url: str, note: str) -> dict[str, str]:
    if status not in LICENSE_STATUSES:
        raise ValueError(f"unknown license status: {status}")
    return {
        "name": name,
        "license": license_name,
        "status": status,
        "evidence_url": evidence_url,
        "note": note,
    }


def classify_flood_maturity(inputs: dict[str, bool]) -> dict[str, Any]:
    """Return the highest defensible maturity level from explicit evidence flags."""
    has_dem = inputs.get("high_resolution_dem", False)
    has_rain = inputs.get("rainfall_timeseries", False)
    has_local_labels = inputs.get("anyang_flood_labels", False)
    has_drainage = inputs.get("authoritative_drainage", False)
    has_calibration = inputs.get("calibration_observations", False)
    if has_dem and has_rain and has_local_labels and has_drainage and has_calibration:
        return {"level": "C", "claim": "quantitative_depth", "reasons": []}
    if has_dem and has_rain and has_local_labels:
        return {
            "level": "B",
            "claim": "locally_validated_relative_hazard",
            "reasons": ["drainage/calibration evidence is incomplete"],
        }
    if has_dem and has_rain:
        return {
            "level": "A",
            "claim": "relative_scenario_hazard",
            "reasons": ["no local flood labels; no quantitative depth claim"],
        }
    return {
        "level": "NONE",
        "claim": "no_flood_output",
        "reasons": ["high-resolution DEM and rainfall time series are required"],
    }


def provenance_record(name: str, provenance: str, source: str, allowed_for_anyang: bool, note: str) -> dict[str, Any]:
    if provenance not in PROVENANCE:
        raise ValueError(f"unknown provenance: {provenance}")
    return {
        "name": name,
        "provenance": provenance,
        "source": source,
        "allowed_for_anyang": allowed_for_anyang,
        "note": note,
    }
