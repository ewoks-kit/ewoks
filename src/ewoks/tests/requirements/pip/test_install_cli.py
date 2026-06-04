import json
import subprocess

import pytest

from ...._requirements.utils.metadata import from_pip_freeze


def test_install_pip_with_freeze(venv):
    with pytest.raises(Exception, match="package is not installed"):
        _ = venv.get_version("ewoksdata")

    requirements = from_pip_freeze.pip_freeze_requirements(["ewoksdata"])

    graph = {
        "graph": {
            "schema_version": "1.1",
            "id": "test_install",
            "requirements": requirements,
        }
    }

    subprocess.check_call(
        [
            "ewoks",
            "install",
            "--yes",
            json.dumps(graph),
            "--package-manager-name",
            "pip",
            "--package-manager-command",
            f"{venv.python} -m pip",
        ]
    )

    assert venv.get_version("ewoksdata")


def test_install_pip_without_freeze(venv):
    with pytest.raises(Exception, match="package is not installed"):
        _ = venv.get_version("ewoksdata")

    requirements = from_pip_freeze.pip_freeze_requirements(["ewoksdata"])
    requirements["distributions"] = [
        {"name": "ewoksdata", "version": ""},
    ]

    graph = {
        "graph": {
            "schema_version": "1.1",
            "id": "test_install",
            "requirements": requirements,
        }
    }

    subprocess.check_call(
        [
            "ewoks",
            "install",
            "--yes",
            json.dumps(graph),
            "--package-manager-name",
            "pip",
            "--package-manager-command",
            f"{venv.python} -m pip",
        ]
    )

    assert venv.get_version("ewoksdata")


def test_install_legacy_pip_freeze(venv):
    with pytest.raises(Exception, match="package is not installed"):
        _ = venv.get_version("ewoksdata")

    requirements = ["ewoksdata"]
    graph = {
        "graph": {
            "schema_version": "1.1",
            "id": "test_install",
            "requirements": requirements,
        }
    }

    subprocess.check_call(
        [
            "ewoks",
            "install",
            "--yes",
            json.dumps(graph),
            "--package-manager-name",
            "pip",
            "--package-manager-command",
            f"{venv.python} -m pip",
        ]
    )

    assert venv.get_version("ewoksdata")


def test_install_without_requirements(venv):
    with pytest.raises(Exception, match="package is not installed"):
        _ = venv.get_version("ewoksdata")

    nodes = [
        {
            "id": 1,
            "task_identifier": 'ewoksdata.tasks.normalization.Normalization"',
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

    subprocess.check_call(
        [
            "ewoks",
            "install",
            "--yes",
            json.dumps(graph),
            "--package-manager-name",
            "pip",
            "--package-manager-command",
            f"{venv.python} -m pip",
        ]
    )

    assert venv.get_version("ewoksdata")
