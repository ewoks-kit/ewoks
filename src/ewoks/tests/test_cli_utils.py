import json
import argparse

import pytest

from ewoks import cliutils


def test_cli_execute_workflow():
    parser = argparse.ArgumentParser()
    cliutils.add_execute_parameters(parser)
    argv = [
        "acyclic1",
        "acyclic2",
        "--test",
        "-p",
        "a=1",
        "-p",
        "task1:b=test",
        "--workflow-dir",
        "/tmp",
    ]
    args = parser.parse_args(argv)
    cliutils.apply_execute_parameters(args)

    assert len(args.graphs) == 2
    assert args.graphs[0]["graph"]["id"] == "acyclic1"
    assert args.graphs[1]["graph"]["id"] == "acyclic2"

    execute_options = {
        "inputs": [
            {"all": False, "name": "a", "value": 1},
            {"id": "task1", "name": "b", "value": "test"},
        ],
        "merge_outputs": False,
        "outputs": [],
        "varinfo": {"root_uri": "", "scheme": "nexus"},
        "load_options": {"root_dir": "/tmp"},
        "execinfo": {},
    }
    assert args.execute_options == execute_options


def test_cli_convert_workflow():
    parser = argparse.ArgumentParser()
    cliutils.add_convert_parameters(parser)
    argv = [
        "acyclic1",
        "test.json",
        "--test",
        "-p",
        "a=1",
        "-p",
        "task1:b=test",
        "--src-format",
        "yaml",
        "--dst-format",
        "json",
    ]
    args = parser.parse_args(argv)
    cliutils.apply_convert_parameters(args)

    assert len(args.graphs) == 1
    assert args.graphs[0]["graph"]["id"] == "acyclic1"

    convert_options = {
        "inputs": [
            {"all": False, "name": "a", "value": 1},
            {"id": "task1", "name": "b", "value": "test"},
        ],
        "load_options": {"representation": "yaml"},
        "save_options": {"representation": "json"},
    }
    assert args.convert_options == convert_options

    argv = ["acyclic1", "test.json"]
    args = parser.parse_args(argv)
    cliutils.apply_convert_parameters(args)

    assert args.destinations == ["test.json"]

    argv = ["acyclic1", ".json"]
    args = parser.parse_args(argv)
    cliutils.apply_convert_parameters(args)

    assert args.destinations == ["acyclic1.json"]

    argv = ["acyclic1", "json"]
    args = parser.parse_args(argv)
    cliutils.apply_convert_parameters(args)

    assert args.destinations == ["acyclic1.json"]


def test_cli_execute_workflow_search(tmp_path, graph_directory):
    parser = argparse.ArgumentParser()
    cliutils.add_execute_parameters(parser)
    argv = [
        str(tmp_path / "subdir" / "*.json"),
        str(tmp_path / "*.json"),
        "--search",
    ]
    args = parser.parse_args(argv)
    cliutils.apply_execute_parameters(args)

    assert len(args.graphs) == 22
    assert args.graphs == graph_directory


def test_cli_convert_workflow_search(tmp_path, graph_directory):
    parser = argparse.ArgumentParser()
    cliutils.add_convert_parameters(parser)
    argv = [
        str(tmp_path / "subdir" / "*.json"),
        str(tmp_path / "*.json"),
        "_suffix.json",
        "--search",
    ]
    args = parser.parse_args(argv)
    cliutils.apply_convert_parameters(args)

    assert len(args.graphs) == 22
    assert args.graphs == graph_directory


@pytest.fixture()
def graph_directory(tmp_path):
    expected_files = list()

    st_mtime = tmp_path.stat().st_mtime

    for i in range(11, 0, -1):
        filename = tmp_path / f"workflow{i}.json"
        expected_files.append(str(filename))
        st_mtime = _create_workflow(filename, {"graph": {"id": f"graph{i}"}}, st_mtime)

    subdir = tmp_path / "subdir"
    subdir.mkdir(parents=True, exist_ok=True)
    for i in range(11, 0, -1):
        filename = tmp_path / f"sub_workflow{i}.json"
        expected_files.append(str(filename))
        st_mtime = _create_workflow(
            filename, {"graph": {"id": f"sub_graph{i}"}}, st_mtime
        )

    return expected_files


def _create_workflow(filename, content, prev_st_mtime):
    while True:
        with open(filename, "w") as f:
            json.dump(content, f)
        st_mtime = filename.stat().st_mtime
        if st_mtime > prev_st_mtime:
            return st_mtime
