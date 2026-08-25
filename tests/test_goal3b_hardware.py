from scripts.evals.goal3b_hardware import audit_hardware


def test_hardware_report_contains_reproducibility_fields():
    report = audit_hardware()
    for key in ("os", "python", "cpu", "memory", "disk", "wsl", "docker", "gpu", "cuda", "project_venv"):
        assert key in report
