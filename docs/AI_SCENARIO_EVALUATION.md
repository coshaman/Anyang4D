# AI scenario evaluation

Run:

```powershell
.venv\Scripts\python.exe scripts/ai/evaluate_goal5a.py
.venv\Scripts\python.exe scripts/ai/train_goal5a.py
```

The evaluation artifact reports median baseline, Ridge, and HistGradientBoosting results; grouped validation/test metrics; intentionally difficult OOD groups; deterministic public-data ablations; direct-target regression errors; and worst-case ranking recovery.
