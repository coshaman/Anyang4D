from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class Provenance(str, Enum):
    OFFICIAL = "OFFICIAL"
    SIMULATED = "SIMULATED"
    OBSERVED_AI = "OBSERVED_AI"
    STALE_OR_UNKNOWN = "STALE_OR_UNKNOWN"


class ProvenanceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provenance: Provenance
    fixture: bool
    items: list[dict[str, Any]] = []
    source_availability: dict[str, dict[str, Any]] = {}


class FoundationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    stage: str
    provenance: Provenance
    fixture: bool
    allowed_provenance: list[Provenance]
    counts: dict[str, int] = {}


class RouteRequest(BaseModel):
    origin: dict[str, float]
    destination: dict[str, float]
