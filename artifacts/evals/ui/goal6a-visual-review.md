# Goal 6A visual review

## Capture set

Real browser screenshots were captured from the running API/frontend without mocking core requests and stored in `artifacts/competition/screenshots/`:

- citizen map
- admin demo opening
- admin mid-timeline
- fixed Scenario A/B
- AI shortlist with exact verification
- provenance/source panel
- citizen large-text view

## Viewport coverage

Existing Playwright visual/accessibility coverage was retained for phone `390x844`, desktop, 200% zoom, reduced motion, and the `768x1024` / `1440x900` matrix. The release capture was run at desktop size for readable evidence; the phone project remains part of the full E2E gate.

## Findings

- Public-service visual language remains restrained teal/cream with no neon AI treatment.
- The AI panel clearly labels AI estimate, support state, exact calls, and exact reference authority.
- The fixed A/B panel exposes numeric deltas and causal scenario inputs.
- Long Korean source names wrap without horizontal overflow in the provenance capture.
- OSM tile requests were aborted during capture; the neutral map canvas, vector overlays, attribution, and data panels remained usable.
- No critical/serious axe violation was observed in the existing admin/citizen release checks.
