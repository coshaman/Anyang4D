# Data and license status — RESET

- NGII 2025 DXF: official provider; source sidecars state a `재배포 금지` restriction. Preserve raw files and do not redistribute them without checking the provider terms.
- NGII 90 m IMG: preserved rejected evidence; not used as street-level terrain.
- OSM: ODbL attribution remains required.
- Public-data catalog pages may be free to download, but each downloaded file still requires its own checksum and license/provenance record.

No new source is promoted to a derived terrain input without a checksum and metadata artifact.

Goal 4A preserves the same provenance boundary. OSM is used for the bounded administrative training graph with ODbL attribution. National shelter and emergency-water records retain official provenance; emergency-water capacity is not inferred. All scenario edits, closures, keyframes, and capacity overrides are `ADMIN_SCENARIO` and are stored as auditable what-if state, never as observed public-safety truth.

The Anyang 2026-07-31 population workbook is an official city source downloaded without login. Its source page states foreign residents are excluded. The processed artifact preserves the source hash and period; only official dong totals are operational inputs. Demo coordinates are a labeled simulated allocation layer because the workbook has no dong polygons.

Goal 5A derived scenarios are simulated administrative data, not observed damage. Model dependencies are scikit-learn 1.6.1 and joblib 1.4.2, both BSD-3-Clause; model metadata records the dependency versions and source hashes.

Goal 6A release policy: the local competition machine may retain the supplied raw NGII DXF/DEM evidence and downloaded source files for audit, subject to provider terms. A public repository/submission bundle must exclude raw NGII DXF/DEM files while retaining the audit metadata, hashes, derived-quality decision, and explicit `TERRAIN_C`/`DROP` boundary. OSM use requires ODbL attribution; the application includes `OpenStreetMap © contributors` and does not redistribute dynamic tiles. The Goal 5A model bundle may be distributed with BSD-3-Clause notices for scikit-learn and joblib.
