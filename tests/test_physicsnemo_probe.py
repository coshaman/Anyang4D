import json
from pathlib import Path

from scripts.evals.physicsnemo_probe import main


def test_physicsnemo_probe_fails_closed_without_dependencies(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main() == 0
    report = json.loads(Path("artifacts/evals/ml/physicsnemo/physicsnemo_probe.json").read_text())
    assert report["product_integration"] is False
    assert report["provenance"] == "SYNTHETIC"
