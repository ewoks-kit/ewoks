import os
import sys

import pytest
from defusedxml import ElementTree
from ewokscore import load_graph
from ewokscore.task import Task
from ewokscore.tests.examples.graphs import graph_names
from ewoksutils.import_utils import import_qualname
from orangewidget.widget import OWBaseWidget

from ..__main__ import main
from .requirements.utils import assert_in_graph_requirements
from .utils import has_default_input
from .utils import no_widget_registry


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

    assert_in_graph_requirements(graph, "ewokscore")


def test_convert_with_all_inputs(tmpdir):
    graph_name = "demo"
    destination = str(tmpdir / f"{graph_name}.json")

    argv = [
        sys.executable,
        "convert",
        graph_name,
        destination,
        "--test",
        "-pa",
        "value=10",
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
        "-pt",
        f"{taskid}:value=test",
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

    not_DAGs = ["acyclic2", "acyclic3", "cyclic1", "self_trigger", "triangle1"]

    if graph_name in not_DAGs:
        with pytest.raises(RuntimeError):
            main(argv=argv, shell=False)
        return

    known_DAGs = ["acyclic1", "demo", "empty", "with_schema"]
    if graph_name not in known_DAGs:
        pytest.skip(f"unknown worklfow {graph_name!r}")

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
