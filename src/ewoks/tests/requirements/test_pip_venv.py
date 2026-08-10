"""Tests specific to the pip-venv package manager."""

import importlib.metadata
import sys

import pytest

from ..._requirements.pip_venv import PipVenvManager
from ..._requirements.utils.requirements_txt import REQUIREMENTS_FILENAME
from .utils import PYTHON_VERSION

pytestmark = pytest.mark.skipif(
    PipVenvManager().version() is None, reason="pip is not installed"
)


def test_default_command():
    manager = PipVenvManager()
    assert manager._cmd_args == (sys.executable,)
    assert repr(manager) == f"PipVenvManager({sys.executable})"


def test_version():
    assert PipVenvManager().version() == importlib.metadata.version("pip")


def test_version_not_available(monkeypatch):
    def not_found(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", not_found)
    assert PipVenvManager().version() is None


def test_never_active():
    """Pip is used when no other package manager is detected."""
    assert PipVenvManager().is_active() is False


def test_gather_requirements_txt():
    """The current environment is described in `requirements.txt` format."""
    requirements = PipVenvManager().gather_requirements()

    lines = requirements.manager.files[REQUIREMENTS_FILENAME].splitlines()
    assert lines
    assert any("ewoks" in requirement for requirement in lines)


def test_create_environment_python_version(env_root, caplog):
    """`venv` cannot provide another python version than the one it runs on."""
    location = env_root / "environment"

    environment = PipVenvManager().create_environment(location, "1.2.3")

    assert "cannot provide python 1.2.3" in caplog.text
    assert environment.python_version() == PYTHON_VERSION
