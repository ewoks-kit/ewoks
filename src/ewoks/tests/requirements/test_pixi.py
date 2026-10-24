"""Tests specific to the pixi package manager."""

import sys

import pytest

from ..._requirements.pixi import PixiManager
from ..._requirements.pixi import PixiRequirements
from ..._requirements.utils.conda_channel import python_specifier
from ..._requirements.utils.files import write_files
from .utils import DISTRIBUTIONS
from .utils import PYTHON_VERSION
from .utils import REQUIREMENTS
from .utils import manager_requirements


def test_workspace_environment(monkeypatch, tmp_path):
    """The environment of a pixi workspace is inside the `.pixi` directory."""
    location = tmp_path / "workspace"
    prefix = location / ".pixi" / "envs" / "default"

    assert PixiManager().environment(location).prefix == prefix

    monkeypatch.setattr(sys, "prefix", str(prefix))
    assert PixiManager().is_active()


def test_files_from_pixi_toml(monkeypatch, tmp_path):
    """The files of the pixi workspace are reused. The pixi.toml takes precedence
    over the pyproject.toml, like pixi itself."""
    files = {"pixi.toml": "# manifest\n", "pixi.lock": "# lock\n"}
    write_files(tmp_path, {**files, "pyproject.toml": "# project\n"})
    monkeypatch.setattr(sys, "prefix", str(tmp_path / ".pixi" / "envs" / "default"))

    assert PixiManager()._gather_files([], PYTHON_VERSION) == files


def test_files_from_pyproject(monkeypatch, tmp_path):
    """Without pixi.toml the pyproject.toml is the manifest of the workspace."""
    files = {"pyproject.toml": "# project\n", "pixi.lock": "# lock\n"}
    write_files(tmp_path, files)
    monkeypatch.setattr(sys, "prefix", str(tmp_path / ".pixi" / "envs" / "default"))

    assert PixiManager()._gather_files([], PYTHON_VERSION) == files


def test_files_from_lock_only(monkeypatch, tmp_path):
    """A lock file without manifest is not reused: no files are stored."""
    write_files(tmp_path, {"pixi.lock": "# lock\n"})
    monkeypatch.setattr(sys, "prefix", str(tmp_path / ".pixi" / "envs" / "default"))

    assert PixiManager()._gather_files([], PYTHON_VERSION) == {}


def test_is_not_active(monkeypatch, tmp_path):
    monkeypatch.delenv("PIXI_PROJECT_ROOT", raising=False)
    monkeypatch.delenv("PIXI_ENVIRONMENT_NAME", raising=False)
    monkeypatch.setattr(sys, "prefix", str(tmp_path))
    assert not PixiManager().is_active()


def test_pixi_environment_name_from_variable(monkeypatch, tmp_path):
    """pixi run and pixi shell set the name of the environment."""
    monkeypatch.setenv("PIXI_ENVIRONMENT_NAME", "test")
    monkeypatch.setattr(sys, "prefix", str(tmp_path / ".pixi" / "envs" / "default"))
    assert PixiManager()._gather_extra_fields() == {"pixi_environment_name": "test"}


def test_pixi_environment_name_from_prefix(monkeypatch, tmp_path):
    """Without the variable, the name comes from the environment prefix."""
    monkeypatch.delenv("PIXI_ENVIRONMENT_NAME", raising=False)
    monkeypatch.setattr(sys, "prefix", str(tmp_path / ".pixi" / "envs" / "test"))
    assert PixiManager()._gather_extra_fields() == {"pixi_environment_name": "test"}


def test_pixi_environment_name_default(monkeypatch, tmp_path):
    """Outside a pixi workspace the environment is "default"."""
    monkeypatch.delenv("PIXI_ENVIRONMENT_NAME", raising=False)
    monkeypatch.setattr(sys, "prefix", str(tmp_path))
    assert PixiManager()._gather_extra_fields() == {}
    requirements = PixiRequirements(**manager_requirements("pixi"))
    assert requirements.manager.pixi_environment_name == "default"


def test_files_environment(tmp_path):
    """The files are installed in the environment of the requirements."""
    data = manager_requirements("pixi")
    data["manager"]["pixi_environment_name"] = "test"
    requirements = PixiRequirements(**data)
    manager = PixiManager()
    environment = manager.files_environment(requirements, manager.environment(tmp_path))
    assert environment.location == tmp_path
    assert environment.prefix == tmp_path / ".pixi" / "envs" / "test"


@pytest.mark.skipif(PixiManager().version() is None, reason="pixi is not installed")
def test_manifest():
    manifest = PixiManager()._manifest(REQUIREMENTS, PYTHON_VERSION)

    assert f'python = "{python_specifier(PYTHON_VERSION)}"' in manifest
    for dist in DISTRIBUTIONS:
        assert f'"{dist.name}" = "=={dist.version}"' in manifest
    assert "platforms = [" in manifest


def test_version_not_available():
    assert PixiManager("pixi-does-not-exist").version() is None
