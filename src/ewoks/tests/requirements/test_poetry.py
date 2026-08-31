"""Tests specific to the poetry package manager."""

import sys

import pytest

from ..._requirements.poetry import PoetryManager
from ..._requirements.poetry import _pyproject
from ..._requirements.utils.base_manager import EWOKS_ENVIRONMENTS_ROOT
from .utils import DISTRIBUTIONS
from .utils import PYTHON_VERSION
from .utils import REQUIREMENTS


def test_pyproject():
    """The project is not a package: there is nothing to build. Dependencies are
    declared in the legacy format, which every supported poetry version reads."""
    pyproject = _pyproject(REQUIREMENTS, PYTHON_VERSION)

    assert "package-mode = false" in pyproject
    assert f'python = "=={PYTHON_VERSION}"' in pyproject
    for dist in DISTRIBUTIONS:
        assert f'"{dist.name}" = "=={dist.version}"' in pyproject
    assert "[project]" not in pyproject


def test_project_environment(monkeypatch, tmp_path):
    """The environment of a poetry project is the `.venv` directory."""
    location = tmp_path / "project"
    prefix = location / ".venv"

    assert PoetryManager().environment(location).prefix == prefix

    monkeypatch.delenv("POETRY_ACTIVE", raising=False)
    monkeypatch.setattr(sys, "prefix", str(prefix))
    assert not PoetryManager().is_active()

    location.mkdir()
    with open(location / "poetry.lock", "w", encoding="utf-8") as fh:
        fh.write("# lock\n")
    assert PoetryManager().is_active()


def test_is_active_poetry_run(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "prefix", str(tmp_path))
    monkeypatch.setenv("POETRY_ACTIVE", "1")
    assert PoetryManager().is_active()


def test_version_not_available():
    assert PoetryManager("poetry-does-not-exist").version() is None


@pytest.mark.skipif(PoetryManager().version() is None, reason="poetry is not installed")
def test_version():
    version = PoetryManager().version()
    assert version[0].isdigit()


@pytest.mark.skipif(PoetryManager().version() is None, reason="poetry is not installed")
def test_environments_root(monkeypatch, tmp_path):
    """Named environments are created where poetry creates them itself."""
    monkeypatch.setenv("POETRY_VIRTUALENVS_PATH", str(tmp_path))

    assert PoetryManager().environments_root() == tmp_path


def test_environments_root_not_available(caplog):
    """Environments of ewoks when poetry cannot provide its environment directory."""
    manager = PoetryManager("poetry-does-not-exist")

    assert manager.environments_root() == EWOKS_ENVIRONMENTS_ROOT

    assert "Cannot determine where poetry creates environments" in caplog.text
