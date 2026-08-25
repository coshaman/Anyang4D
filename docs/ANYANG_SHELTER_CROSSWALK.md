# Anyang shelter crosswalk

The current workspace contains two separate Anyang shelter sources: 224 municipal records and 231 strictly filtered national records. Four national rows containing the substring `안양` but located outside 안양시 were excluded from the operational national layer. The two sources are reconciled for review only and are never summed or silently merged into one operational facility list.

Crosswalk status:

- `EXACT_MATCH`: 24
- `STRONG_MATCH`: 147
- `AMBIGUOUS`: 0
- `LOCAL_ONLY`: 53
- `NATIONAL_ONLY`: 60

Matching uses coordinate-nearest review with a conservative 100 m threshold while retaining each source's name, address, capacity, and provenance. The national `최대수용인원` values are used as official national shelter capacities where present; municipal values remain a separate local-context layer.

Machine-readable source audit: `artifacts/evals/data/goal4b-shelter-crosswalk.json`.
