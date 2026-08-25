from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import FEATURE_SCHEMA_VERSION, MODEL_BUNDLE_VERSION


@dataclass(frozen=True)
class SurrogatePrediction:
    scenario_id: str
    model_version: str = MODEL_BUNDLE_VERSION
    estimated_assigned: float | None = None
    estimated_unserved: float | None = None
    estimated_assignment_cost: float | None = None
    estimated_capacity_deficit: float | None = None
    estimated_overloaded_shelter_count: float | None = None
    ranking_score: float | None = None
    support_status: str = "AI_ESTIMATE_SUPPORTED"
    provenance: str = "AI_SURROGATE"
    exact_verified: bool = False
    exact_result: dict[str, Any] | None = None
    explanation: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "model_version": self.model_version,
            "estimated_assigned": self.estimated_assigned,
            "estimated_unserved": self.estimated_unserved,
            "estimated_assignment_cost": self.estimated_assignment_cost,
            "estimated_capacity_deficit": self.estimated_capacity_deficit,
            "estimated_overloaded_shelter_count": self.estimated_overloaded_shelter_count,
            "ranking_score": self.ranking_score,
            "support_status": self.support_status,
            "provenance": self.provenance,
            "exact_verified": self.exact_verified,
            "exact_result": self.exact_result,
            "explanation": self.explanation,
        }


def validate_feature_schema(features: dict[str, float], expected: list[str]) -> None:
    missing = sorted(set(expected) - set(features))
    extra = sorted(set(features) - set(expected))
    if missing or extra:
        raise ValueError(f"feature schema mismatch: missing={missing}, extra={extra}")


def bundle_metadata(feature_names: list[str], source_hashes: dict[str, str], metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "model_bundle_version": MODEL_BUNDLE_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "feature_names": feature_names,
        "source_hashes": source_hashes,
        "metrics": metrics,
        "provenance": "AI_SURROGATE",
        "exact_verification_required": True,
    }
