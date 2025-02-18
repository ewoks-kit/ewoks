import json
import subprocess

import pytest


def test_install(venv):
    with pytest.raises(Exception, match="package is not installed"):
        venv.get_version("ewoksdata")

    subprocess.check_call(
        [
            "ewoks",
            "install",
            "--yes",
            '{"graph": {"id": "test_install", "requirements": ["ewoksdata"]}}',
            "-p",
            f"{venv.python}",
        ]
    )

    assert venv.get_version("ewoksdata") is not None


def test_install_with_extract(venv):
    with pytest.raises(Exception, match="package is not installed"):
        venv.get_version("ewoksdata")

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
        },  # Check that unsupported task type goes though without error
    ]

    graph = {"graph": {"id": "test_install"}, "nodes": nodes}

    subprocess.check_call(
        [
            "ewoks",
            "install",
            "--yes",
            json.dumps(graph),
            "-p",
            f"{venv.python}",
        ]
    )

    assert venv.get_version("ewoksdata") is not None
