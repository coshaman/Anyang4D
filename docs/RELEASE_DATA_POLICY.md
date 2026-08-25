# Goal 6A release data policy

## Local competition machine

May retain the downloaded official source files, processed artifacts, exact scenario store, OSM snapshots, model bundle, and NGII DXF/DEM evidence for the judging environment. Keep source hashes and provider terms beside the artifacts. Do not treat the NGII terrain evidence as an operational flood input.

## Public repository

Include source code, manifests, processed non-sensitive public-data derivatives, model metadata, evaluation artifacts, license notices, and reproducibility scripts. Exclude raw NGII DXF/DEM packages because their sidecar metadata states redistribution restrictions. Do not commit `.env`, keys, local caches, Playwright traces, or absolute Windows paths.

## Downloadable submission artifact

Package the admin demo, model bundle, processed public-data derivatives, manifests, exact scenarios, claims matrix, evidence summary, and `THIRD_PARTY_NOTICES.md`. Include OSM ODbL attribution, BSD-3-Clause notices for scikit-learn/joblib, and the other third-party dependency notices already present. If a provider's terms are unclear, ship the hash/metadata and require the local competition machine to supply the raw file.

## Explicit exclusions

- Raw NGII DXF and DEM ZIP/IMG evidence from the public bundle.
- Provider-authenticated sources that were not downloaded.
- Any citizen location, real-time population feed, official emergency forecast, or observed-damage label.
- Terrain-derived flood depth or citizen hazard-routing outputs.
