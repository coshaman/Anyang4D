# AI surrogate validation plan

This plan is frozen before final held-out evaluation.

## Status definitions

- `AI_SURROGATE_A`: held-out worst-case Recall@20 ≥ 0.70, Spearman ≥ 0.75, every primary target P95 normalized error ≤ 0.25 where defined, OOD support checks fail closed, and measured AI+top-K exact workflow is faster than exact-all without changing exact results.
- `AI_SURROGATE_B`: useful for research/demo but misses one A criterion; never automatic screening. UI is demo-only and exact verification remains mandatory.
- `AI_SURROGATE_C`: insufficient ranking/generalization, unsafe support behavior, or no measured computational benefit. Do not ship in UI.

Thresholds are fixed before reading final held-out results and may not be relaxed afterward.

## Evaluation

Report MAE, RMSE, R², median absolute error, P90/P95 absolute error, normalized population error, Spearman, NDCG@20, Recall@20, Precision@20, error by scenario family/participation/closure severity/facility outage/capacity deficit, OOD results, ablation results, inference latency, exact-all latency, AI+top-K latency, speedup, and exact calls avoided.
