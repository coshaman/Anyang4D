from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class Provenance(str, Enum):
    OFFICIAL = "OFFICIAL"
    ADMIN_SCENARIO = "ADMIN_SCENARIO"
    SIMULATED = "SIMULATED"
    OBSERVED_AI = "OBSERVED_AI"
    STALE_OR_UNKNOWN = "STALE_OR_UNKNOWN"


DISASTER_TYPES = {"FLOOD", "EARTHQUAKE", "FIRE", "CIVIL_DEFENSE", "GENERAL_EVACUATION"}


@dataclass(frozen=True)
class DemandUnit:
    demand_id: str
    label: str
    latitude: float
    longitude: float
    population: int
    provenance: str
    source_period: str | None = None
    dong_name: str | None = None
    dong_code: str | None = None
    allocation_method: str | None = None
    allocation_provenance: str | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "DemandUnit":
        if int(value["population"]) < 0:
            raise ValueError("population must be non-negative")
        return cls(str(value["demand_id"]), str(value["label"]), float(value["latitude"]), float(value["longitude"]), int(value["population"]), str(value["provenance"]), value.get("source_period"), value.get("dong_name"), value.get("dong_code"), value.get("allocation_method"), value.get("allocation_provenance"))


@dataclass(frozen=True)
class HazardKeyframe:
    time_minute: int
    geometry: dict[str, Any]
    label: str


@dataclass(frozen=True)
class RoadClosureEvent:
    start_minute: int
    end_minute: int
    edge_ids: tuple[str, ...]
    reason: str
    provenance: str


@dataclass(frozen=True)
class FacilityEvent:
    start_minute: int
    end_minute: int
    facility_id: str
    available: bool
    reason: str
    provenance: str


@dataclass(frozen=True)
class CapacityOverride:
    start_minute: int
    end_minute: int
    facility_id: str
    capacity: int
    reason: str
    provenance: str


@dataclass(frozen=True)
class ResourceEvent:
    start_minute: int
    end_minute: int
    resource_id: str
    available: bool
    reason: str
    provenance: str


@dataclass
class Scenario:
    scenario_id: str
    title: str
    disaster_type: str
    start_time: str
    end_time: str
    timestep_minutes: int
    provenance: str
    description: str
    assumptions: list[str] = field(default_factory=list)
    hazard_keyframes: list[HazardKeyframe] = field(default_factory=list)
    road_closure_events: list[RoadClosureEvent] = field(default_factory=list)
    facility_events: list[FacilityEvent] = field(default_factory=list)
    capacity_overrides: list[CapacityOverride] = field(default_factory=list)
    resource_events: list[ResourceEvent] = field(default_factory=list)
    demand_units: list[DemandUnit] = field(default_factory=list)
    affected_demand_ids: list[str] = field(default_factory=list)
    evacuation_fraction: float = 1.0
    affected_demand_rule: str = "HAZARD_CONTAINMENT_OR_EXPLICIT_SELECTION"
    eligible_facility_ids: list[str] = field(default_factory=list)
    audit_log: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Scenario":
        disaster_type = str(value["disaster_type"])
        if disaster_type not in DISASTER_TYPES:
            raise ValueError(f"disaster_type must be one of {sorted(DISASTER_TYPES)}")
        timestep = int(value["timestep_minutes"])
        if timestep <= 0:
            raise ValueError("timestep_minutes must be positive")
        start = datetime.fromisoformat(str(value["start_time"]))
        end = datetime.fromisoformat(str(value["end_time"]))
        if end <= start:
            raise ValueError("end_time must be after start_time")
        participation = float(value.get("evacuation_fraction", 1.0))
        if not 0 <= participation <= 1:
            raise ValueError("evacuation_fraction must be between 0 and 1")
        return cls(
            scenario_id=str(value["scenario_id"]), title=str(value["title"]), disaster_type=disaster_type,
            start_time=start.isoformat(), end_time=end.isoformat(), timestep_minutes=timestep,
            provenance=str(value["provenance"]), description=str(value.get("description", "")),
            assumptions=[str(item) for item in value.get("assumptions", [])],
            hazard_keyframes=[HazardKeyframe(int(item["time"]), dict(item["geometry"]), str(item.get("label", ""))) for item in value.get("hazard_keyframes", [])],
            road_closure_events=[RoadClosureEvent(int(item["start_minute"]), int(item["end_minute"]), tuple(str(edge) for edge in item.get("edge_ids", [])), str(item["reason"]), str(item["provenance"])) for item in value.get("road_closure_events", [])],
            facility_events=[FacilityEvent(int(item["start_minute"]), int(item["end_minute"]), str(item["facility_id"]), bool(item["available"]), str(item["reason"]), str(item["provenance"])) for item in value.get("facility_events", [])],
            capacity_overrides=[CapacityOverride(int(item["start_minute"]), int(item["end_minute"]), str(item["facility_id"]), int(item["capacity"]), str(item["reason"]), str(item["provenance"])) for item in value.get("capacity_overrides", [])],
            resource_events=[ResourceEvent(int(item["start_minute"]), int(item["end_minute"]), str(item["resource_id"]), bool(item["available"]), str(item["reason"]), str(item["provenance"])) for item in value.get("resource_events", [])],
            demand_units=[DemandUnit.from_dict(item) for item in value.get("demand_units", [])],
            affected_demand_ids=[str(item) for item in value.get("affected_demand_ids", [])],
            evacuation_fraction=participation,
            affected_demand_rule=str(value.get("affected_demand_rule", "HAZARD_CONTAINMENT_OR_EXPLICIT_SELECTION")),
            eligible_facility_ids=[str(item) for item in value.get("eligible_facility_ids", [])],
            audit_log=[dict(item) for item in value.get("audit_log", [])],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id, "title": self.title, "disaster_type": self.disaster_type,
            "start_time": self.start_time, "end_time": self.end_time, "timestep_minutes": self.timestep_minutes,
            "provenance": self.provenance, "description": self.description, "assumptions": list(self.assumptions),
            "hazard_keyframes": [{"time": item.time_minute, "geometry": item.geometry, "label": item.label} for item in self.hazard_keyframes],
            "road_closure_events": [asdict(item) | {"edge_ids": list(item.edge_ids)} for item in self.road_closure_events],
            "facility_events": [asdict(item) for item in self.facility_events],
            "capacity_overrides": [asdict(item) for item in self.capacity_overrides],
            "resource_events": [asdict(item) for item in self.resource_events],
            "demand_units": [asdict(item) for item in self.demand_units],
            "affected_demand_ids": list(self.affected_demand_ids),
            "evacuation_fraction": self.evacuation_fraction,
            "affected_demand_rule": self.affected_demand_rule,
            "eligible_facility_ids": list(self.eligible_facility_ids), "audit_log": list(self.audit_log),
        }

    def frame_times(self) -> list[int]:
        duration = int((datetime.fromisoformat(self.end_time) - datetime.fromisoformat(self.start_time)).total_seconds() // 60)
        return list(range(0, duration + 1, self.timestep_minutes))
