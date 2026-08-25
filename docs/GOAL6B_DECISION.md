# Goal 6B submission decision

## Decision

`SUBMISSION_CONTENT_READY = true` for a competition submission candidate based on `COMPETITION_RELEASE_B`.

The frozen product was not changed. Goal 6B reconciled final evidence, corrected stale submission wording, created the 10-page content master and judging artifacts, selected real browser screenshots, and audited claims and package restrictions.

## Authoritative headline values

- Product: 4D administrative public-safety What-if decision support.
- Public data: 224 local shelters, 231 national-filtered shelters, 46 local water, 71 national water, 33 response-material records, 305 AED, 31 dong units / 562,143 residents at 2026-07-31.
- AI: 160 simulated administrative scenarios, 28 pre-solver features, validation Spearman 0.977020, OOD Spearman 0.964430; AI shortlist only and DEMO_ONLY.
- Performance: same-run N=20 exact-all 32,167.964 ms vs hybrid 18,033.545 ms, about 1.78x. Conservative representative real-browser 100-candidate AI+exact timing is 24.889 s; latest warm run 12.408 s is labeled separately.
- A/B: available shelters -1, assignment cost +1,001,955.9 m, assigned/unserved delta 0.

## Strongest arguments

1. Public data changes the computation: population becomes demand, facilities become capacity constraints, and the graph supplies walking costs; provenance remains visible.
2. AI is quantitatively evaluated but never authoritative: it narrows review, exact verifies the selected cases, and its weaker OOD/cost-tail behavior is the reason for DEMO_ONLY.
3. Originality is the auditable combination of time-changing state, capacity-aware evacuation, A/B intervention, public-data reconciliation, AI shortlist and exact verification.

## Remaining weakness and likely judge challenge

The largest weaknesses are absence of official realtime hazard feeds, simulated spatial population anchors, terrain-derived flood path exclusion, external OSM tiles, and batch latency around 25 seconds for 100 candidates. A skeptical judge may ask whether this is operationally deployable; the answer is that it is a bounded competition prototype with a staged, validation-gated roadmap, not an autonomous emergency-response system.

## Human-only actions

Provider redistribution confirmation, applicant identity fields, signatures/stamps, official form/PDF layout review, size-limit check, and final submission remain human actions. Raw NGII DXF/DEM is excluded from the public bundle under the release policy.

## Evidence outputs

`artifacts/evals/submission/evidence-consistency.json` and `claim-audit.json` both PASS. The selected screenshot set is listed in `docs/SUBMISSION_FIGURE_PLAN.md`. No official HWPX/PDF was modified.
