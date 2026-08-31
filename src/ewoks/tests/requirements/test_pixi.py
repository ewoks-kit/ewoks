"""Tests specific to the pixi package manager."""

import sys

import pytest

from ..._requirements.pixi import PixiManager
from ..._requirements.utils.conda_channel import python_specifier
from .utils import DISTRIBUTIONS
from .utils import PYTHON_VERSION
from .utils import REQUIREMENTS


def test_workspace_environment(monkeypatch, tmp_path):
    """The environment of a pixi workspace is inside the `.pixi` directory."""
    location = tmp_path / "workspace"
    prefix = location / ".pixi" / "envs" / "default"

    assert PixiManager().environment(location).prefix == prefix

    monkeypatch.setattr(sys, "prefix", str(prefix))
    assert PixiManager().is_active()


def test_is_not_active(monkeypatch, tmp_path):
    monkeypatch.delenv("PIXI_PROJECT_ROOT", raising=False)
    monkeypatch.delenv("PIXI_ENVIRONMENT_NAME", raising=False)
    monkeypatch.setattr(sys, "prefix", str(tmp_path))
    assert not PixiManager().is_active()


@pytest.mark.skipif(PixiManager().version() is None, reason="pixi is not installed")
def test_manifest():
    manifest = PixiManager()._manifest(REQUIREMENTS, PYTHON_VERSION)

    assert f'python = "{python_specifier(PYTHON_VERSION)}"' in manifest
    for dist in DISTRIBUTIONS:
        assert f'"{dist.name}" = "=={dist.version}"' in manifest
    assert "platforms = [" in manifest


def test_version_not_available():
    assert PixiManager("pixi-does-not-exist").version() is None
