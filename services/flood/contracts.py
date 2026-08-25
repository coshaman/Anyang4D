from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Provenance(str, Enum):
    SYNTHETIC = "SYNTHETIC"
    BENCHMARK = "BENCHMARK"
    ANYANG_OFFICIAL = "ANYANG_OFFICIAL"
    FUTURE_ANYANG = "FUTURE_ANYANG"


class FloodScenarioInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str = Field(min_length=1)
    dem: list[list[float | None]]
    crs: str = Field(min_length=1)
    grid_resolution_m: float = Field(gt=0)
    transform: list[float] = Field(min_length=6, max_length=9)
    rainfall_mm_per_timestep: list[float] = Field(min_length=1)
    timestep_minutes: int = Field(gt=0)
    duration_steps: int = Field(gt=0)
    rainfall_mode: Literal["SCENARIO", "OFFICIAL_WEATHER"]
    provenance: Provenance
    optional_building_mask: list[list[bool]] | None = None
    optional_imperviousness: list[list[float]] | None = None
    optional_drainage_features: list[dict[str, Any]] | None = None

    @model_validator(mode="after")
    def validate_dimensions(self) -> "FloodScenarioInput":
        if not self.dem or not self.dem[0] or any(len(row) != len(self.dem[0]) for row in self.dem):
            raise ValueError("dem must be a non-empty rectangular grid")
        if len(self.rainfall_mm_per_timestep) != self.duration_steps:
            raise ValueError("rainfall length must equal duration_steps")
        if self.rainfall_mode == "OFFICIAL_WEATHER" and self.provenance != Provenance.ANYANG_OFFICIAL:
            raise ValueError("OFFICIAL_WEATHER requires ANYANG_OFFICIAL provenance")
        return self


class FloodScenarioOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str = Field(min_length=1)
    times: list[int] = Field(min_length=1)
    field_kind: Literal["RELATIVE_HAZARD", "FLOOD_CLASS", "WATER_DEPTH_M"]
    frames: list[list[list[float | None]]] = Field(min_length=1)
    crs: str = Field(min_length=1)
    transform: list[float] = Field(min_length=6, max_length=9)
    grid_resolution_m: float = Field(gt=0)
    provenance: Provenance
    fidelity_level: Literal["A", "B", "C"]
    backend: str = Field(min_length=1)
    assumptions: list[str] = []
    limitations: list[str] = []
    bbox: list[float] | None = Field(default=None, min_length=4, max_length=4)

    @model_validator(mode="after")
    def validate_claim(self) -> "FloodScenarioOutput":
        validate_output_claim(self.field_kind, self.fidelity_level, self.provenance)
        if len(self.frames) != len(self.times):
            raise ValueError("frames length must equal times length")
        return self


def validate_output_claim(field_kind: str, fidelity_level: str, provenance: Provenance) -> None:
    if field_kind == "WATER_DEPTH_M" and fidelity_level != "C":
        raise ValueError("WATER_DEPTH_M requires Level C evidence")
    if field_kind == "WATER_DEPTH_M" and provenance != Provenance.ANYANG_OFFICIAL:
        raise ValueError("water depth is not exposed for synthetic or benchmark provenance")
    if provenance == Provenance.ANYANG_OFFICIAL and fidelity_level not in {"A", "B", "C"}:
        raise ValueError("unknown Anyang fidelity level")
