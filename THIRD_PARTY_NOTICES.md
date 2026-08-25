# Third-party notices — Goal 3A evaluation

This file records evaluation dependencies and does not grant rights beyond the upstream terms.

- **OpenStreetMap** — ODbL 1.0; attribution required for the bounded graph and any derived database. [Copyright and license](https://www.openstreetmap.org/copyright).

- **PhysicsNeMo** — Apache License 2.0. [Repository and license statement](https://github.com/NVIDIA/physicsnemo).
- **EPA SWMM** — Public Domain statement in the official repository. [Repository](https://github.com/USEPA/Stormwater-Management-Model).
- **PySWMM** — BSD-2-Clause. [Repository](https://github.com/pyswmm/pyswmm). Optional only.
- **LarNO source** — README claims MIT; root license evidence was not available in the inspected repository listing. HOLD pending authoritative archive.
- **LarNO model and dataset cards** — Hugging Face labels both MIT; benchmark provenance remains UKEA/Futian and MIKE+-generated labels. [Model](https://huggingface.co/holmescao/LarNO), [dataset](https://huggingface.co/datasets/holmescao/LarNO-dataset).

No third-party weights, model source, benchmark data, or flood raster has been copied into the Anyang product tree by Goal 3A.

Goal 5A adds scikit-learn 1.6.1 and joblib 1.4.2 under BSD-3-Clause. They are CPU-only runtime dependencies; no pretrained weights or external model artifacts are used.

Goal 3B uses NumPy for compressed internal frame storage and deterministic calculations under the existing project dependency set. No PhysicsNeMo, PyTorch, LarNO, or SWMM runtime dependency was added to the product environment.
