# AI screening architecture

The admin workflow is:

`SIMULATED_ADMIN_SCENARIO` generation → pre-solver feature extraction → `AI_SURROGATE_ESTIMATE` ranking → exact top-K reference verification → authoritative exact result.

The only AI routes are under `/api/admin/goal5a`. Unsupported feature-range or model/schema states return `AI_ESTIMATE_UNSUPPORTED`; no confidence percentage is fabricated. The citizen surface has no dependency on this router.
