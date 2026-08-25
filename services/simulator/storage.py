from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from .contracts import Scenario


class ScenarioStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, scenario: Scenario, *, action: str = "save", actor: str = "admin") -> Scenario:
        scenario.audit_log.append({"action": action, "actor": actor, "timestamp": datetime.now(timezone.utc).isoformat(), "scenario_id": scenario.scenario_id})
        path = self.root / f"{scenario.scenario_id}.json"
        path.write_text(json.dumps(scenario.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return scenario

    def get(self, scenario_id: str) -> Scenario:
        path = self.root / f"{scenario_id}.json"
        if not path.exists():
            raise FileNotFoundError(scenario_id)
        return Scenario.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list(self) -> list[Scenario]:
        return [self.get(path.stem) for path in sorted(self.root.glob("*.json"))]

    def duplicate(self, scenario_id: str, new_id: str) -> Scenario:
        scenario = self.get(scenario_id)
        value = copy.deepcopy(scenario.to_dict())
        value["scenario_id"] = new_id
        value["title"] = f"{value['title']} 복제"
        duplicate = Scenario.from_dict(value)
        return self.save(duplicate, action="duplicate", actor="admin")

