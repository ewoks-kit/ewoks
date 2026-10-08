"""Tests of the scripts that run `ewoks install` with nothing but a package manager.

The bootstrap environment is prepared in advance so the scripts do not install
anything: its python interpreter runs the ewoks under test.
"""

import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict
from typing import List

import pytest

from .utils import PYTHON_MINOR_VERSION
from .utils import PYTHON_VERSION
from .utils import manager_requirements

_SCRIPTS = Path(__file__).parents[2] / "_bootstrap"
_EWOKS_VERSION = importlib.metadata.version("ewoks")


@pytest.fixture(params=["sh", "powershell"])
def bootstrap_script(request) -> List[str]:
    """Command that runs a bootstrap script."""
    if sys.platform == "win32":
        pytest.skip("the bootstrap environment of the tests needs a POSIX shell")
    if request.param == "sh":
        return ["sh", str(_SCRIPTS / "ewoks-install.sh")]
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell is not installed")
    return [pwsh, "-NoProfile", "-File", str(_SCRIPTS / "ewoks-install.ps1")]


@pytest.fixture
def bootstrap_dir(tmp_path) -> Path:
    """Directory of the bootstrap environments with the environment of the
    ewoks under test for pip-venv."""
    root = tmp_path / "bootstrap"
    location = (
        root / "pip-venv" / f"ewoks-{_EWOKS_VERSION}-python{PYTHON_MINOR_VERSION}"
    )
    python = location / "bin" / "python"
    python.parent.mkdir(parents=True)
    with open(python, "w", encoding="utf-8") as fh:
        fh.write(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
    python.chmod(0o755)
    return root


def test_print_command(bootstrap_script, bootstrap_dir, tmp_path):
    """The bootstrap environment of the ewoks version of the workflow runs
    `ewoks install` with the arguments that are not for the script."""
    workflow = _workflow(tmp_path)
    arguments = [str(workflow), *_pip_venv_arguments(), "--yes"]

    result = _run(bootstrap_script, ["--print-command", *arguments], bootstrap_dir)

    assert result.returncode == 0, result.stderr
    command = result.stdout.strip()
    python = (
        bootstrap_dir
        / "pip-venv"
        / f"ewoks-{_EWOKS_VERSION}-python{PYTHON_MINOR_VERSION}"
        / "bin"
        / "python"
    )
    assert str(python) in command
    assert command.endswith(f"-m ewoks install {' '.join(arguments)}")


def test_run_ewoks_install(bootstrap_script, bootstrap_dir, tmp_path):
    """`ewoks install` runs in the bootstrap environment."""
    workflow = _workflow(tmp_path)
    arguments = [str(workflow), *_pip_venv_arguments(), "--yes", "--in-place"]

    result = _run(bootstrap_script, arguments, bootstrap_dir)

    # The requirements of the workflow have nothing to install
    assert "No distributions provided to install" in result.stderr
    assert f"Install failed for {workflow}" in result.stdout


def test_no_workflow(bootstrap_script, bootstrap_dir):
    result = _run(bootstrap_script, ["--test", "demo"], bootstrap_dir)

    assert result.returncode != 0
    assert "provide the file of the workflow" in result.stderr


def test_unsupported_manager(bootstrap_script, bootstrap_dir, tmp_path):
    workflow = _workflow(tmp_path)

    result = _run(
        bootstrap_script,
        [str(workflow), "--package-manager-name", "unknown"],
        bootstrap_dir,
    )

    assert result.returncode != 0
    assert "package manager 'unknown' is not supported" in result.stderr


def _workflow(tmp_path: Path) -> Path:
    requirements = manager_requirements("pip-venv", python_version=PYTHON_VERSION)
    requirements["ewoks"] = {"version": _EWOKS_VERSION}
    graph = {
        "graph": {"id": "bootstrap", "requirements": requirements},
        "nodes": [],
        "links": [],
    }
    filename = tmp_path / "workflow.json"
    with open(filename, "w", encoding="utf-8") as fh:
        json.dump(graph, fh, indent=2)
    return filename


def _pip_venv_arguments() -> List[str]:
    return [
        "--package-manager-name",
        "pip-venv",
        "--package-manager-command",
        sys.executable,
    ]


def _run(
    script: List[str], arguments: List[str], bootstrap_dir: Path
) -> "subprocess.CompletedProcess[str]":
    env: Dict[str, str] = {**os.environ, "EWOKS_BOOTSTRAP_DIR": str(bootstrap_dir)}
    return subprocess.run(  # noqa: S603 - Script under test
        [*script, *arguments],
        capture_output=True,
        text=True,
        env=env,
        stdin=subprocess.DEVNULL,
        timeout=300,
    )
