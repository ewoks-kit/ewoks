"""Tests specific to the conda package manager."""

import sys

import pytest

from ..._requirements.conda import CondaManager
from ..._requirements.conda import _environment_yml
from ..._requirements.utils.base_manager import EWOKS_ENVIRONMENTS_ROOT
from ..._requirements.utils.conda_channel import python_specifier
from .utils import PYTHON_VERSION
from .utils import REQUIREMENTS


def test_environment_file():
    """Python distributions are declared in the pip section of a conda
    environment file."""
    environment_yml = _environment_yml(REQUIREMENTS, PYTHON_VERSION)

    pip_dependencies = "".join(f"    - {requirement}\n" for requirement in REQUIREMENTS)
    assert (
        environment_yml
        == f"""channels:
  - conda-forge
dependencies:
  - python={python_specifier(PYTHON_VERSION)}
  - pip
  - pip:
{pip_dependencies}"""
    )


def test_environment_file_without_requirements():
    assert (
        _environment_yml([], "")
        == """channels:
  - conda-forge
dependencies:
  - pip
"""
    )


def test_default_command():
    """The fastest implementation available is used."""
    manager = CondaManager()
    assert manager._cmd_args[0] in ("micromamba", "mamba", "conda")


def test_version_not_available():
    assert CondaManager("conda-does-not-exist").version() is None


def test_is_active(monkeypatch, tmp_path):
    monkeypatch.delenv("CONDA_PREFIX", raising=False)
    monkeypatch.setattr(sys, "prefix", str(tmp_path))
    assert not CondaManager().is_active()

    (tmp_path / "conda-meta").mkdir()
    assert CondaManager().is_active()


def test_is_active_conda_prefix(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "prefix", str(tmp_path))
    monkeypatch.setenv("CONDA_PREFIX", str(tmp_path))
    assert CondaManager().is_active()


def test_environments_root():
    """Named environments are created where conda creates them itself."""
    manager = CondaManager()
    if manager.version() is None:
        pytest.skip("conda is not installed")

    root = manager.environments_root()

    assert root.is_absolute()
    assert root != EWOKS_ENVIRONMENTS_ROOT


def test_environments_root_not_available(caplog):
    """Environments of ewoks when conda cannot provide its environment directory."""
    manager = CondaManager("conda-does-not-exist")

    assert manager.environments_root() == EWOKS_ENVIRONMENTS_ROOT

    assert "Cannot determine where conda creates environments" in caplog.text


def test_files_not_available(monkeypatch, tmp_path, caplog):
    """Only a conda environment can be exported."""
    monkeypatch.setattr(sys, "prefix", str(tmp_path))

    assert CondaManager()._gather_files([], PYTHON_VERSION) == {}

    assert "not a conda environment" in caplog.text
