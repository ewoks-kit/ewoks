"""Tests of `ewoks install` for all package managers using the `pip freeze`
requirements format.
"""

import json
import subprocess
import sys

import pytest

from .managers import Environment
from .managers import ManagerCase
from .managers import parametrize_freeze_managers
from .utils import freeze_requirements

pytestmark = parametrize_freeze_managers

_DISTRIBUTION = "ewoksdata"


def test_install_with_freeze(manager_case, environment):
    with pytest.raises(RuntimeError, match="package is not installed"):
        _ = environment.get_version(_DISTRIBUTION)

    requirements = freeze_requirements(manager_case.NAME, [_DISTRIBUTION])

    _install(_graph(requirements), manager_case, environment)

    assert environment.get_version(_DISTRIBUTION)


def test_install_without_freeze(manager_case, environment):
    with pytest.raises(RuntimeError, match="package is not installed"):
        _ = environment.get_version(_DISTRIBUTION)

    requirements = freeze_requirements(
        manager_case.NAME, [], distributions=[{"name": _DISTRIBUTION, "version": ""}]
    )

    _install(_graph(requirements), manager_case, environment)

    assert environment.get_version(_DISTRIBUTION)


def test_install_legacy_pip_freeze(manager_case, environment):
    with pytest.raises(RuntimeError, match="package is not installed"):
        _ = environment.get_version(_DISTRIBUTION)

    _install(_graph([_DISTRIBUTION]), manager_case, environment)

    assert environment.get_version(_DISTRIBUTION)


def test_install_without_requirements(manager_case, environment):
    with pytest.raises(RuntimeError, match="package is not installed"):
        _ = environment.get_version(_DISTRIBUTION)

    nodes = [
        {
            "id": 1,
            "task_identifier": f'{_DISTRIBUTION}.tasks.normalization.Normalization"',
            "task_type": "class",
        },
        {
            "id": 2,
            "task_identifier": "path/to/my/script",
            "task_type": "script",
        },  # Check that unsupported task type goes through without error
    ]

    graph = {
        "graph": {"schema_version": "1.1", "id": "test_install"},
        "nodes": nodes,
    }

    _install(graph, manager_case, environment)

    assert environment.get_version(_DISTRIBUTION)


def _graph(requirements) -> dict:
    return {
        "graph": {
            "schema_version": "1.1",
            "id": "test_install",
            "requirements": requirements,
        }
    }


def _install(graph: dict, manager_case: ManagerCase, environment: Environment) -> None:
    argv = [
        sys.executable,
        "-m",
        "ewoks",
        "install",
        "--yes",
        json.dumps(graph),
        "--package-manager-name",
        manager_case.NAME,
        "--package-manager-command",
        manager_case.cli_command(environment),
    ]
    subprocess.check_call(argv)  # noqa: S603 - Trusted test command;
