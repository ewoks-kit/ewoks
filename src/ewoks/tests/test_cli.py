from ewoksutils.tests.conftest import cli_interface  # noqa F401
from ewoksutils.tests.conftest import graph_directory  # noqa F401

from ..cli_utils import cli_convert_utils


def test_cli_convert(cli_interface):  # noqa F811
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
    cli_args = cli_interface(
        argv,
        cli_convert_utils.convert_arguments,
        cli_convert_utils.parse_convert_arguments,
    )

    assert list(cli_args.graphs) == ["acyclic1"]

    convert_options = {
        "inputs": [
            {"all": False, "name": "a", "value": 1},
            {"id": "task1", "name": "b", "value": "test"},
        ],
        "load_options": {"representation": "test_core"},
        "save_options": {"representation": "json"},
    }
    assert cli_args.convert_options == convert_options

    argv = ["acyclic1", "test.json"]
    cli_args = cli_interface(
        argv,
        cli_convert_utils.convert_arguments,
        cli_convert_utils.parse_convert_arguments,
    )

    assert cli_args.destinations == ["test.json"]

    argv = ["acyclic1", ".json"]
    cli_args = cli_interface(
        argv,
        cli_convert_utils.convert_arguments,
        cli_convert_utils.parse_convert_arguments,
    )

    assert cli_args.destinations == ["acyclic1.json"]

    argv = ["acyclic1", "json"]
    cli_args = cli_interface(
        argv,
        cli_convert_utils.convert_arguments,
        cli_convert_utils.parse_convert_arguments,
    )

    assert cli_args.destinations == ["acyclic1.json"]


def test_cli_convert_search(cli_interface, tmp_path, graph_directory):  # noqa F811
    argv = [
        str(tmp_path / "subdir" / "*.json"),
        str(tmp_path / "*.json"),
        "_suffix.json",
        "--search",
    ]
    cli_args = cli_interface(
        argv,
        cli_convert_utils.convert_arguments,
        cli_convert_utils.parse_convert_arguments,
    )

    assert len(cli_args.graphs) == 22
    assert cli_args.graphs == graph_directory
