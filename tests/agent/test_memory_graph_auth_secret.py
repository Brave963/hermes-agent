import importlib
import os
import sys
from pathlib import Path


def test_memory_graph_auth_generates_per_install_secret(monkeypatch, tmp_path):
    monkeypatch.delenv("MEMORY_GRAPH_SESSION_SECRET", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    sys.modules.pop("agent.memory_graph.auth", None)
    mod = importlib.import_module("agent.memory_graph.auth")
    assert mod.SESSION_SECRET != "mg-default-change-me-in-prod"
    secret_file = tmp_path / ".hermes" / "memory_graph_session_secret"
    assert secret_file.exists()
    assert oct(secret_file.stat().st_mode & 0o777) == "0o600"
    assert secret_file.read_text(encoding="utf-8").strip() == mod.SESSION_SECRET


def test_memory_graph_auth_env_secret_takes_precedence(monkeypatch, tmp_path):
    monkeypatch.setenv("MEMORY_GRAPH_SESSION_SECRET", "test-secret-from-env")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    sys.modules.pop("agent.memory_graph.auth", None)
    mod = importlib.import_module("agent.memory_graph.auth")
    assert mod.SESSION_SECRET == "test-secret-from-env"
    assert not (tmp_path / ".hermes" / "memory_graph_session_secret").exists()
