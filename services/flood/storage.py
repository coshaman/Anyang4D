from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np

from .contracts import FloodScenarioOutput


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")


class FrameStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _scenario_dir(self, scenario_id: str) -> Path:
        if not _SAFE_ID.fullmatch(scenario_id):
            raise ValueError("invalid scenario id")
        return self.root / scenario_id

    def save(self, output: FloodScenarioOutput) -> dict[str, Any]:
        directory = self._scenario_dir(output.scenario_id)
        directory.mkdir(parents=True, exist_ok=True)
        frame_files = []
        for index, (time, frame) in enumerate(zip(output.times, output.frames)):
            filename = f"frame-{index:04d}-{time}.npz"
            values = np.array([[np.nan if value is None else value for value in row] for row in frame], dtype=np.float32)
            np.savez_compressed(directory / filename, values=values)
            frame_files.append({"time": time, "file": filename})
        metadata = output.model_dump(mode="json")
        metadata.pop("frames", None)
        metadata.update({"frame_files": frame_files, "warning": "내부 검증용 자료이며 시민용 안양 홍수 결과가 아닙니다."})
        (directory / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return metadata

    def metadata(self, scenario_id: str) -> dict[str, Any]:
        path = self._scenario_dir(scenario_id) / "metadata.json"
        if not path.exists():
            raise FileNotFoundError(scenario_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def list_scenarios(self) -> list[dict[str, Any]]:
        items = []
        for path in sorted(self.root.iterdir()):
            if path.is_dir() and (path / "metadata.json").exists():
                items.append(self.metadata(path.name))
        return items

    def list_times(self, scenario_id: str) -> list[int]:
        return [int(item["time"]) for item in self.metadata(scenario_id)["frame_files"]]

    def read_frame(self, scenario_id: str, time: int) -> dict[str, Any]:
        metadata = self.metadata(scenario_id)
        entry = next((item for item in metadata["frame_files"] if int(item["time"]) == int(time)), None)
        if entry is None:
            raise FileNotFoundError(f"{scenario_id}:{time}")
        values = np.load(self._scenario_dir(scenario_id) / entry["file"], allow_pickle=False)["values"]
        frame = [[None if not np.isfinite(value) else round(float(value), 6) for value in row] for row in values]
        return {**metadata, "time": int(time), "frame": frame}
