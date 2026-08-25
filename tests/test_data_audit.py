from pathlib import Path

from scripts.data.fetch_sources import sha256_file
from scripts.data.audit_sources import SourceStatus, human_action_block, validate_record
from scripts.data.audit_csv import audit_csv
from scripts.data.audit_osm import build_walk_graph


def test_sha256_is_recorded_for_raw_bytes(tmp_path: Path):
    path = tmp_path / "source.csv"
    path.write_bytes(b"anyang,fixture\n")

    assert sha256_file(path) == "e4d62389f73dc22ed0887875e4664d8020e8e21d9b260253a14e0739bf1d12be"


def test_source_record_rejects_unknown_status():
    try:
        validate_record({"status": "MAYBE"})
    except ValueError as exc:
        assert "MAYBE" in str(exc)
    else:
        raise AssertionError("unknown status was accepted")


def test_human_action_block_contains_required_fields():
    block = human_action_block(
        source="KMA short forecast",
        url="https://example.test",
        why="rainfall input",
        blocker="service key required",
        env="DATA_GO_KR_SERVICE_KEY",
        fallback="disable live weather",
    )

    assert block.startswith("HUMAN_ACTION_REQUIRED")
    assert "Source: KMA short forecast" in block
    assert "Expected env var or local file afterward: DATA_GO_KR_SERVICE_KEY" in block


def test_csv_audit_counts_anyang_rows_and_coordinate_quality(tmp_path: Path):
    path = tmp_path / "source.csv"
    path.write_text("시도명,시군구명,위도,경도,수용인원\n경기도,안양시,37.4,126.9,10\n서울,강남구,37.5,127.0,\n", encoding="utf-8-sig")

    report = audit_csv(path)

    assert report["raw_row_count"] == 2
    assert report["anyang_row_count"] == 1
    assert report["coordinate_valid_count"] == 2
    assert report["columns"] == ["시도명", "시군구명", "위도", "경도", "수용인원"]


def test_osm_audit_builds_walkable_edges_and_connectivity():
    payload = {
        "elements": [
            {"type": "node", "id": 1, "lat": 37.4, "lon": 126.9},
            {"type": "node", "id": 2, "lat": 37.401, "lon": 126.901},
            {"type": "node", "id": 3, "lat": 37.402, "lon": 126.902},
            {"type": "way", "id": 10, "nodes": [1, 2, 3], "tags": {"highway": "footway"}},
        ]
    }

    report = build_walk_graph(payload)

    assert report["node_count"] == 3
    assert report["edge_count"] == 2
    assert report["component_count"] == 1
