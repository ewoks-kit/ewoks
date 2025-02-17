import os
import sys

import pytest
from ewokscore import load_graph
from ewokscore.graph import TaskGraph
from ewokscore.tests.examples.graphs import get_graph
from ewokscore.tests.examples.graphs import graph_names
from ewokscore.tests.utils.results import assert_execute_graph_default_result

from ewoks.__main__ import main
from ewoks.tests.utils import has_default_input


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
    assert has_default_input(task1_node, "b", 42)

    assert graph.graph.graph["requirements"] is not None
    assert _ewokscore_in_graph_requirements(graph)


def test_execute_with_convert_destination_inputs_all(tmpdir):
    destination = str(tmpdir / "convert.json")
    argv = [
        sys.executable,
        "execute",
        "demo",
        "--test",
        "-p",
        "b=42",
        "--inputs=all",
        "-o",
        f"convert_destination={destination}",
    ]

    main(argv=argv, shell=False)
    assert os.path.exists(destination)

    graph = load_graph(destination)

    for node in graph.graph.nodes.values():
        assert has_default_input(node, "b", 42)

    assert graph.graph.graph["requirements"] is not None
    assert _ewokscore_in_graph_requirements(graph)
