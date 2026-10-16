"""Tests of the scripts that run `ewoks install` with nothing but a package manager.

The workflows are saved by `ewoks convert`. A fake bootstrap environment is
prepared in advance so the scripts do not install anything: its python interpreter
runs the ewoks under test, which is not on the python package index. Except for
the tests marked `package_manager_install`, which install package managers and
ewoks from the internet.
"""

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import pytest

from ...bindings import convert_graph
from ...bindings import load_graph
from .utils import PYTHON_MINOR_VERSION

_SCRIPTS = Path(__file__).parents[2] / "_bootstrap"
_INSTALLABLE_MANAGERS = ["uv", "pixi", "poetry", "conda"]


@pytest.fixture(params=["sh", "pwsh", "powershell"])
def script(request) -> List[str]:
    """Command that runs a bootstrap script. `powershell` is Windows PowerShell 5.1."""
    if request.param == "sh":
        if sys.platform == "win32":
            pytest.skip("sh is not available on Windows")
        return ["sh", str(_SCRIPTS / "ewoks-install.sh")]
    if request.param == "powershell" and sys.platform != "win32":
        pytest.skip("Windows PowerShell is only available on Windows")
    powershell = shutil.which(request.param)
    if powershell is None:
        pytest.skip(f"{request.param} is not installed")
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
    system tools, which can include package managers (see `_skip_if_installed`)."""
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
            _python_wrapper(bin_dir / name)
        directories = [str(bin_dir), "/usr/bin", "/bin", "/usr/sbin", "/sbin"]
    path = os.pathsep.join(directories)
    env = {
        name: value
        for name, value in os.environ.items()
        if name not in ("VIRTUAL_ENV", "CONDA_PREFIX")
    }
    env["PATH"] = path
    return env


@pytest.fixture(scope="module")
def saved_workflow(tmp_path_factory) -> Callable[[str], Path]:
    """Workflow saved by `ewoks convert` in a format: json, yaml or ows. Every
    format is saved once because generating the requirements takes seconds."""
    directory = tmp_path_factory.mktemp("workflows")
    workflows: Dict[str, Path] = {}

    def get(workflow_format: str) -> Path:
        if workflow_format not in workflows:
            workflows[workflow_format] = _save_workflow(directory, workflow_format)
        return workflows[workflow_format]

    return get


@pytest.fixture
def workflow(saved_workflow) -> Path:
    """Workflow saved by `ewoks convert` in JSON."""
    return saved_workflow("json")


@pytest.fixture
def bootstrap_dir(tmp_path, workflow) -> Path:
    """Directory of the bootstrap environments with a fake pip-venv environment
    for the workflow."""
    root = tmp_path / "boot strap"
    _fake_bootstrap_environment(root, workflow)
    return root


def test_print_command(script, workflow, bootstrap_dir):
    """The bootstrap environment of the ewoks version of the workflow runs
    `ewoks install` with the arguments that are not for the script."""
    arguments = [str(workflow), *_pip_venv_arguments(), "--yes"]

    result = _run(script, ["--print-command", *arguments], bootstrap_dir)

    assert result.returncode == 0, result.stderr
    command = result.stdout.strip()
    python = _bootstrap_python(bootstrap_dir, workflow)
    assert str(python) in command
    assert command.endswith(f"-m ewoks install {' '.join(arguments)}")


def test_run_ewoks_install(script, workflow, bootstrap_dir, tmp_path):
    """`ewoks install` runs in the bootstrap environment and prints how to run it
    again before its summary."""
    # A directory that is not a python environment, so nothing is installed
    env_root = tmp_path / "envs"
    (env_root / "bootstrap").mkdir(parents=True)
    arguments = [
        str(workflow),
        *_pip_venv_arguments(),
        "--yes",
        "--clean",
        "--env-root",
        str(env_root),
    ]

    result = _run(script, arguments, bootstrap_dir)

    assert "is not a python environment" in result.stderr
    python = _bootstrap_python(bootstrap_dir, workflow)
    header, summary = result.stdout.split("Install failed for")
    assert "Bootstrap environment" in header
    assert str(python) in header
    assert f"-m ewoks install {workflow}" in header.replace("'", "")


def test_manager_command_with_spaces(script, workflow, bootstrap_dir, tmp_path):
    """The package manager command is quoted like the one of `ewoks install`."""
    if script[0] != "sh":
        pytest.skip("PowerShell splits the command like `ewoks install` on Windows")
    python = tmp_path / "python bin" / "python"
    python.parent.mkdir()
    _python_wrapper(python)
    arguments = [
        str(workflow),
        "--package-manager-name",
        "pip-venv",
        "--package-manager-command",
        shlex.quote(str(python)),
    ]

    result = _run(script, ["--print-command", *arguments], bootstrap_dir)

    assert result.returncode == 0, result.stderr
    assert "@python=" in result.stdout


def test_installed_manager_with_spaces(workflow, no_managers_env, tmp_path):
    """The package manager installed by the script is passed to `ewoks install`
    quoted for the shell."""
    _skip_if_installed("uv", no_managers_env)
    if sys.platform == "win32":
        pytest.skip("sh is not available on Windows")
    bootstrap_dir = tmp_path / "boot strap"
    uv = bootstrap_dir / "package-managers" / "uv" / "bin" / "uv"
    uv.parent.mkdir(parents=True)
    uv.write_text("#!/bin/sh\nexit 1\n")
    uv.chmod(0o755)
    _fake_bootstrap_environment(bootstrap_dir, workflow, manager="uv")

    result = _run(
        ["sh", str(_SCRIPTS / "ewoks-install.sh")],
        ["--print-command", str(workflow), "--package-manager-name", "uv"],
        bootstrap_dir,
        env=no_managers_env,
    )

    assert result.returncode == 0, result.stderr
    command = shlex.split(result.stdout)
    manager_command = command[command.index("--package-manager-command") + 1]
    assert shlex.split(manager_command) == [str(uv)]


def test_relative_workflow(script, workflow, bootstrap_dir):
    """`ewoks install` gets the absolute path of the workflow."""
    result = _run(
        script,
        ["--print-command", workflow.name, *_pip_venv_arguments()],
        bootstrap_dir,
        cwd=workflow.parent,
    )

    assert result.returncode == 0, result.stderr
    assert f"-m ewoks install {workflow}" in result.stdout.replace("'", "")


def test_no_workflow(script, tmp_path):
    result = _run(script, ["--test", "demo"], tmp_path / "bootstrap")

    assert result.returncode != 0
    assert "provide the file of the workflow" in result.stderr


def test_unsupported_manager(script, workflow, tmp_path):

    result = _run(
        script,
        [str(workflow), "--package-manager-name", "unknown"],
        tmp_path / "bootstrap",
    )

    assert result.returncode != 0
    assert "package manager 'unknown' is not supported" in result.stderr


def test_install_manager_requires_name(script, workflow, tmp_path):

    result = _run(
        script,
        [str(workflow), "--install-package-manager"],
        tmp_path / "bootstrap",
    )

    assert result.returncode != 0
    assert "--install-package-manager requires --package-manager-name" in (
        result.stderr
    )


def test_manager_not_installed(script, workflow, no_managers_env, tmp_path):
    _skip_if_installed("pixi", no_managers_env)

    result = _run(
        script,
        [str(workflow), "--package-manager-name", "pixi"],
        tmp_path / "bootstrap",
        env=no_managers_env,
    )

    assert result.returncode != 0
    assert "pixi is not installed (see --install-package-manager)" in result.stderr


def test_install_conda_in_directory_with_spaces(
    script, workflow, no_managers_env, tmp_path
):
    _skip_if_installed("conda", no_managers_env)
    result = _run(
        script,
        [
            "--install-package-manager",
            str(workflow),
            "--package-manager-name",
            "conda",
        ],
        tmp_path / "boot strap",
        env=no_managers_env,
    )

    assert result.returncode != 0
    assert "Miniforge cannot be installed in a directory with spaces" in result.stderr
    assert "install conda in" not in result.stderr


@pytest.mark.package_manager_install
@pytest.mark.parametrize("manager", _INSTALLABLE_MANAGERS)
def test_install_manager(script, workflow, no_managers_env, tmp_path, manager):
    """The package manager is installed in the bootstrap directory, used again
    by the next run and passed to `ewoks install`."""
    _skip_if_installed(manager, no_managers_env)
    if manager == "conda":
        # Miniforge cannot be installed in a directory with spaces
        bootstrap_dir = tmp_path / "bootstrap"
    else:
        # A directory with a space, like the home directory of some Windows users
        bootstrap_dir = tmp_path / "boot strap"
    arguments = [
        "--print-command",
        "--bootstrap-requirement",
        "ewoks",
        str(workflow),
        "--package-manager-name",
        manager,
        "--yes",
    ]

    result = _run(
        script,
        ["--install-package-manager", *arguments],
        bootstrap_dir,
        env=no_managers_env,
        timeout=1800,
    )

    assert result.returncode == 0, result.stderr
    assert f"install {manager} in" in result.stderr
    manager_dir = bootstrap_dir / "package-managers" / manager
    command = result.stdout.strip()
    if sys.platform == "win32":
        # `ewoks install` splits the command on spaces that are not escaped
        assert str(manager_dir).replace(" ", "\\ ") in command
    else:
        assert str(manager_dir) in command

    result = _run(script, arguments, bootstrap_dir, env=no_managers_env)

    assert result.returncode == 0, result.stderr
    assert f"install {manager} in" not in result.stderr
    assert result.stdout.strip() == command


@pytest.mark.parametrize("workflow_format", ["json", "yaml", "ows"])
def test_requirements_of_any_format(script, saved_workflow, tmp_path, workflow_format):
    """The bootstrap environment of the ewoks version and the engine of the
    workflow is used, whatever the format of the workflow."""
    workflow = saved_workflow(workflow_format)
    bootstrap_dir = tmp_path / "bootstrap"
    python = _fake_bootstrap_environment(bootstrap_dir, workflow)

    result = _run(
        script,
        ["--print-command", str(workflow), *_pip_venv_arguments()],
        bootstrap_dir,
    )

    assert result.returncode == 0, result.stderr
    assert "install ewoks" not in result.stderr
    assert str(python) in result.stdout


def _skip_if_installed(manager: str, env: Dict[str, str]) -> None:
    """Skip a test that needs a package manager to be missing from the PATH."""
    if shutil.which(manager, path=env["PATH"]):
        pytest.skip(f"{manager} is installed in a system directory")


def _fake_bootstrap_environment(
    root: Path, workflow: Path, manager: str = "pip-venv"
) -> Path:
    """Bootstrap environment of a workflow, as the scripts cache it, whose python
    interpreter is the one of the tests. The scripts find the ewoks under test
    installed in it, so they do not install anything. Returns the python
    interpreter."""
    if sys.platform == "win32":
        pytest.skip("the fake bootstrap environment is a POSIX shell script")
    python = _bootstrap_python(root, workflow, manager)
    python.parent.mkdir(parents=True)
    _python_wrapper(python)
    return python


def _bootstrap_python(root: Path, workflow: Path, manager: str = "pip-venv") -> Path:
    """Python interpreter of the bootstrap environment of a workflow."""
    ewoks = load_graph(str(workflow)).graph.graph["requirements"]["ewoks"]
    engine = ewoks["engine"]
    name = (
        f"ewoks={ewoks['version']}@{engine['name']}={engine['version']}"
        f"@python={PYTHON_MINOR_VERSION}"
    )
    return root / manager / name / "bin" / "python"


def _python_wrapper(path: Path) -> None:
    """POSIX shell script that runs the python interpreter of the tests."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
    path.chmod(0o755)


def _save_workflow(directory: Path, workflow_format: str) -> Path:
    """Workflow saved by `ewoks convert` with its requirements."""
    if workflow_format == "ows":
        pytest.importorskip("ewoksorange")
    filename = directory / f"workflow.{workflow_format}"
    convert_graph(
        {"graph": {"id": "bootstrap"}, "nodes": [], "links": []},
        str(filename),
        package_manager_name="pip-venv",
        package_manager_command=(sys.executable,),
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
    cwd: Optional[Path] = None,
) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(  # noqa: S603 - Script under test
        [*script, "--bootstrap-dir", str(bootstrap_dir), *arguments],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        timeout=timeout,
    )
