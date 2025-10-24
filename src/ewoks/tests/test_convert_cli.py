import os
import sys
from xml.etree import ElementTree

import pytest
from ewokscore import load_graph
from ewokscore.graph import TaskGraph
from ewokscore.task import Task
from ewokscore.tests.examples.graphs import graph_names
from ewoksutils.import_utils import import_qualname
from orangewidget.widget import OWBaseWidget

from ewoks.__main__ import main
from ewoks.tests.utils import has_default_input
from ewoks.tests.utils import no_widget_registry


def _ewokscore_in_graph_requirements(graph: TaskGraph) -> bool:
    ewokscore_in_req = False
    for requirement in graph.graph.graph["requirements"]:
        if "ewokscore" in requirement:
            ewokscore_in_req = True
            break

    return ewokscore_in_req


@pytest.mark.parametrize("graph_name", graph_names())
def test_convert_to_json(graph_name, tmpdir):
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


def test_convert_with_all_inputs(tmpdir):
    graph_name = "demo"
    destination = str(tmpdir / f"{graph_name}.json")

    argv = [
        sys.executable,
        "convert",
        graph_name,
        destination,
        "--test",
        "-p",
        "value=10",
        "--inputs=all",
    ]

    main(argv=argv, shell=False)
    assert os.path.exists(destination)

    graph = load_graph(destination)
    for node in graph.graph.nodes.values():
        assert has_default_input(node, "value", 10)


def test_convert_with_taskid_inputs(tmpdir):
    graph_name = "demo"
    destination = str(tmpdir / f"{graph_name}.json")
    taskid = "ewokscore.tests.examples.tasks.sumtask.SumTask"

    argv = [
        sys.executable,
        "convert",
        graph_name,
        destination,
        "--test",
        "-p",
        f"{taskid}:value=test",
        "--input-node-id",
        "taskid",
    ]

    main(argv=argv, shell=False)
    assert os.path.exists(destination)

    graph = load_graph(destination)
    for node in graph.graph.nodes.values():
        if node["task_identifier"] == taskid:
            assert has_default_input(node, "value", "test")


@pytest.mark.parametrize("graph_name", graph_names())
def test_convert_to_ows(graph_name, tmpdir):
    destination = str(tmpdir / f"{graph_name}.ows")
    argv = [
        sys.executable,
        "convert",
        graph_name,
        destination,
        "--test",
    ]

    DAGs = ["acyclic1", "demo", "empty"]
    if graph_name not in DAGs:
        with pytest.raises(RuntimeError):
            main(argv=argv, shell=False)
        return

    # Run `convert`
    with no_widget_registry():
        main(argv=argv, shell=False)
    assert os.path.exists(destination)

    tree = ElementTree.parse(destination)
    root = tree.getroot()

    for node in root.findall("./nodes/node"):
        try:
            assert issubclass(import_qualname(node.get("qualified_name")), OWBaseWidget)
        except ImportError:
            assert issubclass(import_qualname(node.get("name")), Task)
