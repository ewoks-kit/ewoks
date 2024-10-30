import os
import sys
import pytest

from ewoks.__main__ import main
from ewokscore import load_graph
from ewokscore.graph import TaskGraph
from ewokscore.tests.examples.graphs import graph_names


def _ewokscore_in_graph_requirements(graph: TaskGraph) -> bool:
    ewokscore_in_req = False
    for requirement in graph.graph.graph["requirements"]:
        if "ewokscore" in requirement:
            ewokscore_in_req = True
            break

    return ewokscore_in_req


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
