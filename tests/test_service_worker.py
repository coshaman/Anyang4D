from pathlib import Path


def test_service_worker_never_intercepts_api_and_invalidates_old_shell():
    source = (Path(__file__).parents[1] / "public/sw.js").read_text(encoding="utf-8")
    assert 'safe-twin-anyang-shell-v3' in source
    assert 'url.pathname.startsWith("/api/")' in source
    assert 'self.skipWaiting()' in source
    assert 'self.clients.claim()' in source
    assert 'event.request.mode === "navigate"' in source
