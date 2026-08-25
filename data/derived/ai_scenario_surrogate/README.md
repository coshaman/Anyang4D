# Goal 5A derived corpus

`labels.jsonl` is generated only from explicit `SIMULATED_ADMIN_SCENARIO` candidates and the frozen Goal 4B exact reference engine. Each row is a `REFERENCE_SIMULATION_LABEL`, not observed damage or a forecast. `manifest.json` records source hashes and the reference-engine version.

Generate or resume:

```powershell
.venv\Scripts\python.exe scripts/ai/generate_goal5a_dataset.py --seed 5 --count 160
```
