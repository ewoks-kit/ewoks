"""Tests specific to the uv package manager."""

import os
import shutil
import sys
from pathlib import Path
from typing import Iterator

import pytest

from ..._requirements.utils.environment import Environment
from ..._requirements.uv import UvManager
from .utils import PYTHON_VERSION


@pytest.fixture
def uv_environment(tmp_path) -> Iterator[Environment]:
    """Environment of a uv project."""
    if UvManager().version() is None:
        pytest.skip("uv is not installed")
    location = tmp_path / "environment"
    yield UvManager().create_environment(location)
    shutil.rmtree(location, ignore_errors=True)


@pytest.fixture
def no_uv_environment(monkeypatch, tmp_path) -> Iterator[Path]:
    """Python environment that was not created by uv and is not a uv project."""
    monkeypatch.delenv("UV", raising=False)
    prefix = tmp_path / "project" / "prefix"
    prefix.mkdir(parents=True)
    with open(prefix / "pyvenv.cfg", "w", encoding="utf-8") as fh:
        fh.write(f"home = {os.path.dirname(sys.executable)}\n")
    monkeypatch.setattr(sys, "prefix", str(prefix))
    yield prefix


def test_default_command():
    manager = UvManager()
    assert manager._cmd_args == ("uv",)
    assert repr(manager) == "UvManager(uv)"


def test_version_not_available():
    assert UvManager("uv-does-not-exist").version() is None


def test_files_not_available(caplog):
    """Without a lock file the environment is reproduced from the distributions."""
    manager = UvManager("uv-does-not-exist")

    assert manager._gather_files([], PYTHON_VERSION) == {}

    assert "uv cannot describe the current python environment" in caplog.text


def test_project_environment(uv_environment):
    """The environment of a uv project is the `.venv` directory."""
    assert uv_environment.prefix == uv_environment.location / ".venv"
    assert Environment.from_location(uv_environment.location) == uv_environment


def test_is_active_uv_environment(uv_environment, monkeypatch):
    monkeypatch.delenv("UV", raising=False)
    monkeypatch.setattr(sys, "prefix", str(uv_environment.prefix))
    assert UvManager().is_active()


def test_is_active_uv_run(no_uv_environment, monkeypatch):
    """`uv run` provides the uv executable through the environment."""
    assert not UvManager().is_active()
    monkeypatch.setenv("UV", "/path/to/uv")
    assert UvManager().is_active()


def test_is_active_uv_project(no_uv_environment, monkeypatch):
    """The environment is inside a uv project."""
    assert not UvManager().is_active()
    with open(no_uv_environment.parent / "uv.lock", "w", encoding="utf-8") as fh:
        fh.write("version = 1\n")
    assert UvManager().is_active()


def test_is_not_active(no_uv_environment):
    assert not UvManager().is_active()
