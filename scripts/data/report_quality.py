from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.data.audit_csv import audit_csv
from scripts.data.audit_osm import audit_osm_file


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/manifests/data_manifest.json"
REPORT_DIR = ROOT / "artifacts/evals/data"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audits: dict[str, Any] = {}
    for record in manifest["datasets"]:
        local = record.get("local_path")
        if not local:
            continue
        path = ROOT / local
        if not path.exists():
            record["quality_error"] = "manifest local_path does not exist"
            continue
        if path.suffix.lower() == ".csv":
            audit = audit_csv(path)
        elif path.suffix.lower() == ".json" and "osm" in record["id"]:
            audit = audit_osm_file(path)
        else:
            continue
        audits[record["id"]] = audit
        record["schema_columns"] = audit.get("columns")
        if "anyang_row_count" in audit:
            record["anyang_feature_count"] = audit["anyang_row_count"]
        if "osm_element_count" not in record and "element_count" in audit:
            record["osm_element_count"] = audit["element_count"]
        record["quality_artifact"] = f"artifacts/evals/data/{record['id']}.json"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    for dataset_id, audit in audits.items():
        (REPORT_DIR / f"{dataset_id}.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    downloaded = [r for r in manifest["datasets"] if r.get("status") in {"DOWNLOADED", "UP_TO_DATE"}]
    blocked = [r for r in manifest["datasets"] if r.get("status") == "HUMAN_AUTH_REQUIRED"]
    lines = [
        "# SAFE-Twin Anyang Goal 1 data quality report",
        "",
        "Generated from `data/manifests/data_manifest.json` by `scripts/data/report_quality.py`.",
        "All counts below are measured from raw bytes or the provider response; titles are not treated as evidence.",
        "",
        "## Acquisition summary",
        "",
        f"- Manifest records: {len(manifest['datasets'])}",
        f"- Downloaded or up-to-date: {len(downloaded)}",
        f"- Human/provider access blockers: {len(blocked)}",
        "",
        "## Measured datasets",
        "",
    ]
    for dataset_id, audit in audits.items():
        record = next(r for r in manifest["datasets"] if r["id"] == dataset_id)
        lines += [f"### {record['dataset_title']}", "", f"- Status: `{record['status']}`", f"- Raw path: `{record.get('local_path')}`"]
        if "raw_row_count" in audit:
            lines += [f"- Raw rows: {audit['raw_row_count']}", f"- Rows containing 안양/Anyang: {audit['anyang_row_count']}", f"- Encoding: `{audit['encoding']}`"]
            lines += [f"- Coordinate columns: `{audit['coordinate_columns']}`", f"- Valid WGS84 coordinate pairs: {audit['coordinate_valid_count']}", f"- Projected coordinate columns: `{audit['projected_coordinate_columns']}`", f"- Valid projected pairs: {audit['projected_coordinate_valid_count']}"]
            lines += [f"- Numeric quality: `{audit['numeric_quality']}`"]
        else:
            lines += [f"- OSM elements: {audit['element_count']}", f"- Graph nodes: {audit['node_count']}", f"- Graph edges: {audit['edge_count']}", f"- Connected components: {audit['component_count']}", f"- Largest component fraction: {audit['largest_component_fraction']:.6f}"]
        lines.append("")
    lines += ["## Blockers", ""]
    for record in blocked:
        lines += [f"- `{record['id']}`: {record.get('blocker', 'provider access required')}; expected `{record.get('expected_env_var', 'provider credential')}`."]
    lines += ["", "## Goal 3 flood viability", "", "The currently acquired layers establish shelter/water/AED point coverage and a connected OSM pedestrian graph. They do not establish a flood model: Anyang flood traces, authoritative buildings, population grids, land cover, and DEM remain unavailable or access-gated. Proceeding to Goal 3 requires either the documented provider credentials or an explicit model-scope decision accepting those missing layers.", ""]
    (ROOT / "docs/DATA_QUALITY_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
