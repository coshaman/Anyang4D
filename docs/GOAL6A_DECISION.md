# Goal 6A release decision

## Decision

`COMPETITION_RELEASE_B` — viable submission candidate with live-demo caveats.

## Why

The frozen Goal 4B exact engine and Goal 5A demo-only AI path passed the release readiness, data consistency, reproducibility, real HTTP, browser, build, audit, and accessibility gates. The live path is usable, but the startup cold run was 15.380 seconds, the 100-candidate AI+exact browser step was 24.889 seconds, external OSM tiles can be unavailable, and N=1000 scale was not measured because feature extraction exceeded a practical benchmark window. These are manageable presentation caveats, not grounds for a release-C decision.

## Frozen safety boundary

- `FINAL_TERRAIN_CLASS=TERRAIN_C`
- `STREET_LEVEL_FLOOD_TERRAIN_PATH=DROP`
- `CITIZEN_HAZARD_ROUTING_FROM_TERRAIN=DROP`
- `AI_SURROGATE_B`
- `ADMIN_AI_SCENARIO_SCREENING=DEMO_ONLY`
- exact Goal 4B engine remains the final verifier

## Remaining human-only actions

Before public submission, confirm provider redistribution terms for each downloaded public-data derivative and keep raw NGII evidence only on the local competition machine unless NGII grants redistribution permission. No account login, DNS, key issuance, or CAPTCHA blocker was encountered in this goal.
