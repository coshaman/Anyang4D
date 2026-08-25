from __future__ import annotations

import hashlib
import math

import numpy as np


def frozen_plan_sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spatial_group_key(point: tuple[float, float], block_size_m: float) -> tuple[int, int]:
    if block_size_m <= 0:
        raise ValueError("block_size_m must be positive")
    return math.floor(point[0] / block_size_m), math.floor(point[1] / block_size_m)


def seam_statistics(left: list[float], right: list[float]) -> dict[str, float | int]:
    if len(left) != len(right) or not left:
        raise ValueError("seam sides must have the same non-empty sample count")
    difference = np.abs(np.asarray(left, dtype=float) - np.asarray(right, dtype=float))
    return {"count": int(len(difference)), "median_m": float(np.median(difference)), "p95_m": float(np.percentile(difference, 95))}


def spatial_group_split(records: list[dict[str, object]], test_ids: set[str], block_size_m: float) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    held = [record for record in records if record["id"] in test_ids]
    held_blocks = {spatial_group_key((float(record["x"]), float(record["y"])), block_size_m) for record in held}
    test = [record for record in records if spatial_group_key((float(record["x"]), float(record["y"])), block_size_m) in held_blocks]
    train = [record for record in records if record not in test]
    return train, test
