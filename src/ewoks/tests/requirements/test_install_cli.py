"""Tests of `ewoks install`, which does not depend on the package manager."""

import json
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from typing import List
from typing import Optional

import pytest

from ..._requirements import environment_name
from ..._requirements.utils.environment import Environment
from ...bindings import load_graph
from .managers import ManagerCase
from .utils import DISTRIBUTIONS
from .utils import PYTHON_VERSION
from .utils import REQUIREMENTS
from .utils import assert_installed
from .utils import manager_requirements

_GRAPH_ID = "test_install"
"""Identifier of the workflows to install, which is also the name of the
environment created for them."""


def test_install_with_files(fast_manager_case, env_root):
    files = fast_manager_case.native_files(DISTRIBUTIONS, PYTHON_VERSION)
    if not files:
        pytest.skip(f"{fast_manager_case.NAME} cannot generate its requirement files")
    requirements = manager_requirements(
        fast_manager_case.NAME,
        files=files,
        distributions=DISTRIBUTIONS,
        python_version=PYTHON_VERSION,
    )

    with _install(_graph(requirements), fast_manager_case, env_root) as location:
        assert_installed(Environment.from_location(location), DISTRIBUTIONS)


def test_install_without_files(fast_manager_case, env_root):
    requirements = manager_requirements(
        fast_manager_case.NAME, distributions=DISTRIBUTIONS
    )

    with _install(_graph(requirements), fast_manager_case, env_root) as location:
        assert_installed(Environment.from_location(location), DISTRIBUTIONS)


def test_install_legacy_requirements_list(fast_manager_case, env_root):
    requirements = REQUIREMENTS

    with _install(_graph(requirements), fast_manager_case, env_root) as location:
        assert_installed(Environment.from_location(location), DISTRIBUTIONS)


def test_install_without_requirements(fast_manager_case, env_root):
    """Requirements are guessed from the workflow nodes."""
    nodes = [
        {
            "id": 1,
            # The distribution that provides this module is installed
            "task_identifier": "six.moves.range",
            "task_type": "method",
        },
        {
            "id": 2,
            "task_identifier": "path/to/my/script",
            "task_type": "script",
        },  # Check that unsupported task type goes through without error
    ]
    graph = {
        "graph": {"schema_version": "1.1", "id": _GRAPH_ID},
        "nodes": nodes,
    }

    with _install(graph, fast_manager_case, env_root) as location:
        assert Environment.from_location(location).distribution_version("six")


def test_install_env_name(fast_manager_case, env_root):
    """The environment name replaces the workflow identifier."""
    graph = _graph(REQUIREMENTS)

    with _install(graph, fast_manager_case, env_root, env_name="myenv") as location:
        assert location == env_root / "myenv"
        assert_installed(Environment.from_location(location), DISTRIBUTIONS)


def test_install_default_location(fast_manager_case, isolated_home):
    """Without a root directory the package manager provides the location."""
    graph = _graph(REQUIREMENTS, graph_id=f"{_GRAPH_ID}_{fast_manager_case.NAME}")

    with _install(graph, fast_manager_case) as location:
        assert isolated_home in location.parents
        assert_installed(Environment.from_location(location), DISTRIBUTIONS)


def test_default_location_without_workflow_id(fast_manager_case, isolated_home):
    """Workflows without an id do not share a location."""
    first = _location({"graph": {"label": "first"}}, fast_manager_case)
    second = _location({"graph": {"label": "second"}}, fast_manager_case)

    assert first != second
    assert first.parent == second.parent


def test_install_existing_environment(fast_manager_case, env_root):
    """An existing environment is installed in, unless it is cleaned first."""
    graph = _graph(REQUIREMENTS)

    with _install(graph, fast_manager_case, env_root) as location:
        marker = location / "marker.txt"
        marker.touch()

        _run_install(graph, fast_manager_case, env_root)
        assert marker.exists()

        _run_install(graph, fast_manager_case, env_root, clean=True)
        assert not marker.exists()
        assert_installed(Environment.from_location(location), DISTRIBUTIONS)


def test_clean_without_environment(fast_manager_case, env_root):
    """Only a python environment is removed."""
    graph = _graph(REQUIREMENTS)
    location = _location(graph, fast_manager_case, env_root)
    location.mkdir(parents=True)
    argv = _argv(fast_manager_case, env_root, clean=True) + [json.dumps(graph)]

    result = subprocess.run(  # noqa: S603 - Trusted test command
        argv, capture_output=True, text=True, check=False
    )

    assert "is not a python environment" in result.stdout + result.stderr
    assert not list(location.iterdir())


def test_install_single_workflow_per_name(fast_manager_case, env_root):
    graph = json.dumps(_graph(REQUIREMENTS))
    argv = _argv(fast_manager_case, env_root, env_name="myenv") + [graph, graph]

    result = subprocess.run(  # noqa: S603 - Trusted test command
        argv, capture_output=True, text=True, check=False
    )

    assert result.returncode != 0
    assert "'--env-name' requires a single workflow" in result.stderr


def test_install_in_place_without_environment(fast_manager_case, env_root):
    """Installing in the current python environment does not create one."""
    argv = _argv(fast_manager_case, env_root) + ["--in-place", json.dumps(_graph([]))]

    result = subprocess.run(  # noqa: S603 - Trusted test command
        argv, capture_output=True, text=True, check=False
    )

    assert result.returncode != 0
    assert "'--in-place' cannot be combined" in result.stderr


def _graph(requirements, graph_id: str = _GRAPH_ID) -> dict:
    return {
        "graph": {
            "schema_version": "1.1",
            "id": graph_id,
            "requirements": requirements,
        }
    }


def _location(
    graph: dict,
    manager_case: ManagerCase,
    env_root: Optional[Path] = None,
    env_name: Optional[str] = None,
) -> Path:
    """Location of the environment that `ewoks install` creates for this workflow."""
    name = env_name or environment_name(load_graph(graph))
    return manager_case.manager().environment_location(name, env_root)


def _argv(
    manager_case: ManagerCase,
    env_root: Optional[Path] = None,
    env_name: Optional[str] = None,
    clean: bool = False,
) -> List[str]:
    argv = [
        sys.executable,
        "-m",
        "ewoks",
        "install",
        "--yes",
        "--package-manager-name",
        manager_case.NAME,
    ]
    if manager_case.command():
        argv += ["--package-manager-command", manager_case.cli_command()]
    if env_root:
        argv += ["--env-root", str(env_root)]
    if env_name:
        argv += ["--env-name", env_name]
    if clean:
        argv += ["--clean"]
    return argv


@contextmanager
def _install(
    graph: dict,
    manager_case: ManagerCase,
    env_root: Optional[Path] = None,
    env_name: Optional[str] = None,
    clean: bool = False,
) -> Iterator[Path]:
    """Install a workflow and remove the environment it created, also when it was
    not created inside `env_root`."""
    location = _location(graph, manager_case, env_root, env_name)
    try:
        _run_install(graph, manager_case, env_root, env_name, clean)
        yield location
    finally:
        shutil.rmtree(location, ignore_errors=True)


def _run_install(
    graph: dict,
    manager_case: ManagerCase,
    env_root: Optional[Path] = None,
    env_name: Optional[str] = None,
    clean: bool = False,
) -> None:
    argv = _argv(manager_case, env_root, env_name, clean) + [json.dumps(graph)]
    subprocess.check_call(argv)  # noqa: S603 - Trusted test command
