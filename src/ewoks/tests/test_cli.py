import os
import json
import subprocess
import sys
import pytest

from ewoks.__main__ import main
from ewokscore import load_graph
from ewokscore.graph import TaskGraph
from ewokscore.tests.examples.graphs import graph_names
from ewokscore.tests.examples.graphs import get_graph
from ewokscore.tests.utils.results import assert_execute_graph_default_result


def _ewokscore_in_graph_requirements(graph: TaskGraph) -> bool:
    ewokscore_in_req = False
    for requirement in graph.graph.graph["requirements"]:
        if "ewokscore" in requirement:
            ewokscore_in_req = True
            break

    return ewokscore_in_req


@pytest.mark.parametrize("graph_name", graph_names())
@pytest.mark.parametrize("scheme", (None, "json"))
@pytest.mark.parametrize("engine", (None, "dask", "ppf"))
def test_execute(graph_name, scheme, engine, tmpdir):
    if graph_name == "self_trigger":
        pytest.skip(
            "Self-triggering workflow execution is inconsistent: https://gitlab.esrf.fr/workflow/ewoks/ewoksppf/-/issues/16"
        )

    graph, expected = get_graph(graph_name)
    argv = [sys.executable, "execute", graph_name, "--test", "--merge-outputs"]
    if engine:
        argv += ["--engine", engine]
    if engine == "ppf":
        argv += ["--outputs", "end"]
    else:
        argv += ["--outputs", "all"]
    if scheme:
        argv += ["--data-root-uri", str(tmpdir), "--data-scheme", scheme]
        varinfo = {"root_uri": str(tmpdir), "scheme": scheme}
    else:
        varinfo = None

    keep = graph
    ewoksgraph = load_graph(graph)
    non_dag = ewoksgraph.is_cyclic or ewoksgraph.has_conditional_links

    results = main(argv=argv, shell=False)
    assert len(results) == 1

    if non_dag and engine != "ppf":
        assert isinstance(results[0], RuntimeError)
    else:
        assert_execute_graph_default_result(ewoksgraph, results[0], expected, varinfo)
        assert keep == graph


@pytest.mark.parametrize("graph_name", graph_names())
def test_convert(graph_name, tmpdir):
    destination = str(tmpdir / f"{graph_name}.json")
    argv = [
        sys.executable,
        "convert",
        graph_name,
        destination,
        "--test",
        "-s",
        "indent=2",
    ]
    main(argv=argv, shell=False)
    assert os.path.exists(destination)

    graph = load_graph(destination)
    assert graph.graph.graph["requirements"] is not None
    assert _ewokscore_in_graph_requirements(graph)


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


def test_execute_with_convert_destination(tmpdir):
    destination = str(tmpdir / "convert.json")
    argv = [
        sys.executable,
        "execute",
        "demo",
        "--test",
        "-p",
        "task1:b=42",
        "-o",
        f"convert_destination={destination}",
    ]

    main(argv=argv, shell=False)
    assert os.path.exists(destination)

    graph = load_graph(destination)

    task1_node = graph.graph.nodes["task1"]
    assert task1_node["default_inputs"][-1] == {
        "name": "b",
        "value": 42,
    }

    assert graph.graph.graph["requirements"] is not None
    assert _ewokscore_in_graph_requirements(graph)
