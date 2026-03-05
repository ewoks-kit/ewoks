import json
import sys

from ewoks.__main__ import main


def test_lint_demo(capsys):
    main(argv=[sys.executable, "lint", "demo", "--test"], shell=False)
    captured = capsys.readouterr()

    assert captured.out == "Workflow demo linted without errors!\n"
    assert captured.err == ""


def test_lint_incorrect_graph(capsys):
    graph = {
        "graph": {"id": "test"},
        "nodes": [{"task_identifier": "a.python.task", "task_type": "klass"}],
    }
    graph_as_str = json.dumps(graph)
    main(argv=[sys.executable, "lint", json.dumps(graph)], shell=False)
    captured = capsys.readouterr()

    assert f"Workflow {graph_as_str} has validation errors!" in captured.out
    assert (
        "Input should be 'class', 'generated', 'method', 'graph', 'ppfmethod', 'ppfport', 'script' or 'notebook'"
        in captured.out
    )
