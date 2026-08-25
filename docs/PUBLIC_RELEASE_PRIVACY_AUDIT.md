# Public release privacy audit

The public tree must not contain participant identity details, addresses, phone numbers, signatures, `.env` files, API keys, local caches, real citizen locations, or absolute Windows paths. The supplied private submission bundle is retained only under `artifacts/final/private-source/`, which is excluded from the public release policy and must never be committed or uploaded.

Missing identity fields remain visibly human-owned in the official working copy. No participant name, contact, signature, consent, or certificate is inferred.

Run `python scripts/evals/audit_public_release.py` before creating a public repository or deployment archive. The resulting JSON is the release gate.
