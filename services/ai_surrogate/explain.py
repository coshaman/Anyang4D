from __future__ import annotations

from typing import Any


def explain_features(features: dict[str, float], metadata: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    mean = metadata.get("support_mean", [])
    std = metadata.get("support_std", [])
    names = metadata["feature_names"]
    ranked = sorted(((abs((features[name] - mean[index]) / max(std[index], 1e-9)), name, features[name]) for index, name in enumerate(names)), reverse=True)[:limit]
    return [{"feature": name, "value": round(float(value), 4), "relative_magnitude": round(float(magnitude), 4), "text": f"{name} 입력이 학습 분포 중심에서 상대적으로 크게 벗어나 우선 검토 순위에 영향을 준 입력"} for magnitude, name, value in ranked]
