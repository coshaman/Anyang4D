"""Read-only hardware and ML environment audit for Goal 3B."""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import ctypes
from pathlib import Path
from typing import Any


def _command(command: list[str], timeout: float = 3.0) -> str | None:
    try:
        result = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    raw = result.stdout or result.stderr or b""
    output = raw.decode("utf-8", errors="replace").strip()
    return output or None


def audit_hardware() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    disk = shutil.disk_usage(root)
    torch_spec = importlib.util.find_spec("torch")
    memory = {"windows_total_bytes": None, "windows_available_bytes": None}
    if platform.system() == "Windows":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_uint32), ("memory_load", ctypes.c_uint32), ("total", ctypes.c_uint64), ("available", ctypes.c_uint64), ("total_page", ctypes.c_uint64), ("available_page", ctypes.c_uint64), ("total_virtual", ctypes.c_uint64), ("available_virtual", ctypes.c_uint64), ("available_extended", ctypes.c_uint64)]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            memory = {"windows_total_bytes": status.total, "windows_available_bytes": status.available}
    report: dict[str, Any] = {
        "os": {"system": platform.system(), "release": platform.release(), "version": platform.version(), "machine": platform.machine()},
        "python": {"version": platform.python_version(), "executable": sys.executable},
        "cpu": {"logical_count": os.cpu_count(), "processor": platform.processor()},
        "memory": memory,
        "disk": {"root": str(root), "free_bytes": disk.free, "total_bytes": disk.total},
        "wsl": {"available": shutil.which("wsl") is not None, "version": _command(["wsl", "--status"])},
        "docker": {"available": shutil.which("docker") is not None, "version": _command(["docker", "--version"])},
        "gpu": {"nvidia_smi": shutil.which("nvidia-smi") is not None, "details": _command(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])},
        "cuda": {"torch_available": torch_spec is not None, "torch_cuda": None},
        "project_venv": {"path": str(root / ".venv"), "exists": (root / ".venv").is_dir(), "torch_installed": torch_spec is not None},
    }
    if torch_spec is not None:
        import torch

        report["cuda"].update({"torch_version": torch.__version__, "torch_cuda": torch.version.cuda, "cuda_available": torch.cuda.is_available()})
    output = root / "artifacts/evals/ml/goal3b-hardware.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(audit_hardware(), indent=2))
