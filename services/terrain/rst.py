from __future__ import annotations

import importlib.util
import shutil


def inspect_rst_backend() -> dict[str, object]:
    grass = shutil.which("grass") or shutil.which("grass84") or shutil.which("grass83")
    qgis = shutil.which("qgis_process")
    scipy = importlib.util.find_spec("scipy") is not None
    if grass:
        return {"status": "AVAILABLE_NOT_RUN", "executable": grass, "reason": "adapter deliberately does not invoke an external GIS process during the bounded rescue"}
    return {"status": "METHOD_B_NOT_RUN", "grass_available": False, "qgis_process_available": bool(qgis), "scipy_available": scipy, "reason": "no GRASS/QGIS RST implementation or compatible spline backend is available; no unverified substitute was run"}

