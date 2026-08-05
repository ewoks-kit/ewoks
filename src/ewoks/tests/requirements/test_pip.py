"""Tests specific to the pip package manager."""

import importlib.metadata
import sys

import pytest

from ..._requirements.pip import PipManager

pytestmark = pytest.mark.skipif(
    PipManager().version() is None, reason="pip is not installed"
)


def test_default_command():
    manager = PipManager()
    assert manager._cmd_args == (sys.executable, "-m", "pip")
    assert repr(manager) == f"PipManager({sys.executable}, -m, pip)"


def test_version():
    assert PipManager().version() == importlib.metadata.version("pip")


def test_version_not_available(monkeypatch):
    def not_found(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", not_found)
    assert PipManager().version() is None


def test_never_active():
    """Pip is used when no other package manager is detected."""
    assert PipManager().is_active() is False
