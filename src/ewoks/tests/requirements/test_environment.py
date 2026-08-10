"""Tests of the python environment layouts."""

import sys
from pathlib import Path

import pytest

from ..._requirements.utils.environment import ENVIRONMENT_SUBDIRS
from ..._requirements.utils.environment import Environment

_INTERPRETERS = [
    ("linux", Path("bin", "python")),
    ("win32", Path("Scripts", "python.exe")),
    ("win32", Path("python.exe")),
]
"""Interpreter locations inside an environment prefix, per platform."""


@pytest.mark.parametrize("subdir", ENVIRONMENT_SUBDIRS)
@pytest.mark.parametrize("platform, relative", _INTERPRETERS)
def test_environment_layout(platform, relative, subdir, monkeypatch, tmp_path):
    """Every interpreter location is found in every environment layout."""
    monkeypatch.setattr(sys, "platform", platform)
    prefix = tmp_path / subdir if subdir else tmp_path
    python = prefix / relative
    python.parent.mkdir(parents=True, exist_ok=True)
    python.touch()

    environment = Environment.from_location(tmp_path)

    assert environment.location == tmp_path
    assert environment.prefix == prefix
    assert environment.python == python


def test_no_environment(tmp_path):
    with pytest.raises(ValueError, match="No python environment found"):
        Environment.from_location(tmp_path)
