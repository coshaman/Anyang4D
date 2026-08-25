# Public release license and provenance audit

Release policy: publish source code, processed lawful public-data derivatives, model metadata, evaluation artifacts, and provenance notices. Do not publish raw NGII DXF/DEM or the private submission bundle.

- OSM data uses ODbL 1.0 attribution; see `THIRD_PARTY_NOTICES.md` and `https://www.openstreetmap.org/copyright`.
- Public-data derivatives retain provider landing URLs and retrieval metadata in `data/manifests/data_manifest.json`; each provider's current reuse terms must be rechecked before publication.
- NGII raw terrain files remain local evidence only. Their acquisition branch is closed and no release feature depends on them.
- Python model dependencies retain their package notices. Optional unlicensed or unevaluated research modules are not shipped as product claims.

The machine-readable gate is `artifacts/final/public-release-manifest.json`; a non-empty finding blocks publication.
