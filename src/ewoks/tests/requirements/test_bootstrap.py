"""Tests of the scripts that run `ewoks install` with nothing but a package manager.

The bootstrap environment is prepared in advance so the scripts do not install
anything: its python interpreter runs the ewoks under test. Except for the tests
marked `package_manager_install`, which install package managers and ewoks from
the internet.
"""

import html
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional

import pytest
import yaml

from .utils import PYTHON_MINOR_VERSION
from .utils import PYTHON_VERSION
from .utils import manager_requirements

_SCRIPTS = Path(__file__).parents[2] / "_bootstrap"
_EWOKS_VERSION = importlib.metadata.version("ewoks")
_INSTALLABLE_MANAGERS = ["uv", "pixi", "poetry", "conda"]


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


@pytest.fixture(params=["sh", "powershell"])
def any_platform_script(request) -> List[str]:
    """Command that runs a bootstrap script on any platform."""
    if request.param == "sh":
        if sys.platform == "win32":
            pytest.skip("sh is not available on Windows")
        return ["sh", str(_SCRIPTS / "ewoks-install.sh")]
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if powershell is None:
        pytest.skip("PowerShell is not installed")
    return [
        powershell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(_SCRIPTS / "ewoks-install.ps1"),
    ]


@pytest.fixture
def no_managers_env(tmp_path) -> Dict[str, str]:
    """Environment variables with a PATH that only provides python and the
    system tools."""
    if sys.platform == "win32":
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        directories = [
            os.path.dirname(sys.executable),
            os.path.join(system_root, "System32"),
            system_root,
            os.path.join(system_root, "System32", "WindowsPowerShell", "v1.0"),
        ]
    else:
        bin_dir = tmp_path / "python-bin"
        bin_dir.mkdir()
        for name in ("python3", f"python{PYTHON_MINOR_VERSION}"):
            python = bin_dir / name
            with open(python, "w", encoding="utf-8") as fh:
                fh.write(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
            python.chmod(0o755)
        directories = [str(bin_dir), "/usr/bin", "/bin", "/usr/sbin", "/sbin"]
    path = os.pathsep.join(directories)
    for manager in _INSTALLABLE_MANAGERS:
        if shutil.which(manager, path=path):
            pytest.skip(f"{manager} is installed in a system directory")
    env = {
        name: value
        for name, value in os.environ.items()
        if name not in ("VIRTUAL_ENV", "CONDA_PREFIX")
    }
    env["PATH"] = path
    return env


@pytest.fixture
def bootstrap_dir(tmp_path) -> Path:
    """Directory of the bootstrap environments with the environment of the
    ewoks under test for pip-venv."""
    root = tmp_path / "bootstrap"
    _bootstrap_python(root, _EWOKS_VERSION)
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


def test_install_manager_requires_name(any_platform_script, tmp_path):
    workflow = _workflow(tmp_path)

    result = _run(
        any_platform_script,
        [str(workflow), "--install-package-manager"],
        tmp_path / "bootstrap",
    )

    assert result.returncode != 0
    assert "--install-package-manager requires --package-manager-name" in (
        result.stderr
    )


def test_manager_not_installed(any_platform_script, no_managers_env, tmp_path):
    workflow = _workflow(tmp_path)

    result = _run(
        any_platform_script,
        [str(workflow), "--package-manager-name", "pixi"],
        tmp_path / "bootstrap",
        env=no_managers_env,
    )

    assert result.returncode != 0
    assert "pixi is not installed (see --install-package-manager)" in result.stderr


@pytest.mark.package_manager_install
@pytest.mark.parametrize("manager", _INSTALLABLE_MANAGERS)
def test_install_manager(any_platform_script, no_managers_env, tmp_path, manager):
    """The package manager is installed in the bootstrap directory, used again
    by the next run and passed to `ewoks install`."""
    workflow = _workflow(tmp_path)
    bootstrap_dir = tmp_path / "bootstrap"
    arguments = [
        "--print-command",
        "--ewoks-requirement",
        "ewoks",
        str(workflow),
        "--package-manager-name",
        manager,
        "--yes",
    ]

    result = _run(
        any_platform_script,
        ["--install-package-manager", *arguments],
        bootstrap_dir,
        env=no_managers_env,
        timeout=1800,
    )

    assert result.returncode == 0, result.stderr
    assert f"install {manager} in" in result.stderr
    manager_dir = bootstrap_dir / "package-managers" / manager
    command = result.stdout.strip()
    assert f"--package-manager-command {manager_dir}" in command.replace("'", "")

    result = _run(any_platform_script, arguments, bootstrap_dir, env=no_managers_env)

    assert result.returncode == 0, result.stderr
    assert f"install {manager} in" not in result.stderr
    assert result.stdout.strip() == command


@pytest.mark.parametrize("workflow_format", ["json", "yaml", "ows"])
def test_requirements_of_any_format(bootstrap_script, tmp_path, workflow_format):
    """The bootstrap environment of the ewoks version and the engine of the
    workflow is used, whatever the format of the workflow."""
    engine_version = importlib.metadata.version("ewokscore")
    engine = {"name": "ewokscore", "version": engine_version}
    workflow = _workflow(tmp_path, workflow_format, engine=engine)
    bootstrap_dir = tmp_path / "bootstrap"
    python = _bootstrap_python(
        bootstrap_dir, f"{_EWOKS_VERSION}-ewokscore-{engine_version}"
    )

    result = _run(
        bootstrap_script,
        ["--print-command", str(workflow), *_pip_venv_arguments()],
        bootstrap_dir,
    )

    assert result.returncode == 0, result.stderr
    assert "install ewoks" not in result.stderr
    assert str(python) in result.stdout


def _bootstrap_python(root: Path, tag: str) -> Path:
    """Python interpreter of a pip-venv bootstrap environment that runs the ewoks
    under test."""
    location = root / "pip-venv" / f"ewoks-{tag}-python{PYTHON_MINOR_VERSION}"
    python = location / "bin" / "python"
    python.parent.mkdir(parents=True)
    with open(python, "w", encoding="utf-8") as fh:
        fh.write(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
    python.chmod(0o755)
    return python


def _workflow(
    tmp_path: Path, workflow_format: str = "json", engine: Optional[dict] = None
) -> Path:
    requirements = manager_requirements("pip-venv", python_version=PYTHON_VERSION)
    requirements["ewoks"] = {"version": _EWOKS_VERSION, "engine": engine}
    graph = {
        "graph": {"id": "bootstrap", "requirements": requirements},
        "nodes": [],
        "links": [],
    }
    filename = tmp_path / f"workflow.{workflow_format}"
    with open(filename, "w", encoding="utf-8") as fh:
        if workflow_format == "json":
            # The engine comes before the ewoks version
            json.dump(graph, fh, indent=2, sort_keys=True)
        elif workflow_format == "yaml":
            yaml.safe_dump(graph, fh)
        else:
            # Orange workflows embed the graph attributes as JSON
            graph_attrs = html.escape(json.dumps(graph["graph"]), quote=False)
            fh.write(
                f"<scheme>\n<ewoks_graph_attrs>{graph_attrs}</ewoks_graph_attrs>\n</scheme>\n"
            )
    return filename


def _pip_venv_arguments() -> List[str]:
    return [
        "--package-manager-name",
        "pip-venv",
        "--package-manager-command",
        sys.executable,
    ]


def _run(
    script: List[str],
    arguments: List[str],
    bootstrap_dir: Path,
    env: Optional[Dict[str, str]] = None,
    timeout: float = 300,
) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(  # noqa: S603 - Script under test
        [*script, "--bootstrap-dir", str(bootstrap_dir), *arguments],
        capture_output=True,
        text=True,
        env=env,
        stdin=subprocess.DEVNULL,
        timeout=timeout,
    )
