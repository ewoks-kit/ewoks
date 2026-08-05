"""Tests specific to the uv package manager."""

import os
import shutil
import sys
from typing import Iterator

import pytest

from ..._requirements.uv import UvManager
from .managers import Environment
from .managers import UvCase


@pytest.fixture
def uv_environment(tmp_path) -> Iterator[Environment]:
    if UvManager().version() is None:
        pytest.skip("uv is not installed")
    path = tmp_path / "environment"
    try:
        yield UvCase().create_environment(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def no_uv_environment(monkeypatch, tmp_path) -> Iterator[str]:
    """Python environment that was not created by uv."""
    monkeypatch.delenv("UV", raising=False)
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    with open(prefix / "pyvenv.cfg", "w", encoding="utf-8") as fh:
        fh.write(f"home = {os.path.dirname(sys.executable)}\n")
    monkeypatch.setattr(sys, "prefix", str(prefix))
    yield str(prefix)


def test_default_command():
    manager = UvManager()
    assert manager._executable == ("uv",)
    assert manager._options == ("--python", sys.executable)


def test_command_options():
    manager = UvManager("/path/to/uv", "--python", "/path/to/python")
    assert manager._executable == ("/path/to/uv",)
    assert manager._options == ("--python", "/path/to/python")
    assert repr(manager) == "UvManager(/path/to/uv, --python, /path/to/python)"


def test_version_not_available():
    assert UvManager("uv-does-not-exist").version() is None


def test_is_active_uv_environment(uv_environment, monkeypatch):
    monkeypatch.delenv("UV", raising=False)
    monkeypatch.setattr(sys, "prefix", str(uv_environment.path))
    assert UvManager().is_active()


def test_is_active_uv_run(no_uv_environment, monkeypatch):
    """`uv run` provides the uv executable through the environment."""
    assert not UvManager().is_active()
    monkeypatch.setenv("UV", "/path/to/uv")
    assert UvManager().is_active()


def test_is_not_active(no_uv_environment):
    assert not UvManager().is_active()
