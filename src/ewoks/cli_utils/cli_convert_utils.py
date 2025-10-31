from argparse import Namespace
from typing import List

from ewoksutils.cli_utils import cli_arguments
from ewoksutils.cli_utils import cli_log_utils
from ewoksutils.cli_utils import cli_parse
from ewoksutils.cli_utils.cli_spec import CLIArg

from .._engines import get_graph_representations
from .cli_parse import parse_destinations


def convert_arguments(
    shell: bool = False, default_log_level: str = "warning"
) -> List[CLIArg]:
    if shell:
        args_list = cli_log_utils.log_arguments(default_log_level=default_log_level)
    else:
        args_list = []

    args_list += cli_arguments.workflow_arguments("convert")
    args_list += cli_arguments.ewoks_inputs_arguments()
    args_list += [
        CLIArg(
            "destination",
            [],
            type=str,
            help="Destination of the conversion (e.g., JSON filename).",
        ),
        CLIArg(
            "source_representation",
            ["--src-format"],
            type=str.lower,
            choices=get_graph_representations(),
            help="Source format.",
        ),
        CLIArg(
            "destination_representation",
            ["--dst-format"],
            type=str.lower,
            choices=get_graph_representations(),
            help="Destination format.",
        ),
        CLIArg(
            "load_options",
            ["-o", "--load-option"],
            action="append",
            metavar="OPTION=VALUE",
            help="Load options.",
        ),
        CLIArg(
            "save_options",
            ["-s", "--save-option"],
            action="append",
            metavar="OPTION=VALUE",
            help="Save options.",
        ),
        CLIArg(
            "exclude_requirements",
            ["--exclude-requirements"],
            action="store_true",
            help="Do not include the packages of the current Python environment as requirements in the destination workflow.",
        ),
    ]
    return args_list


def parse_convert_arguments(cli_args: Namespace, shell: bool = False) -> None:
    if shell:
        cli_log_utils.parse_log_arguments(cli_args)
    cli_args.workflows, cli_args.graphs = cli_parse.parse_workflows(cli_args)
    cli_args.destinations = parse_destinations(cli_args)

    load_options = dict(cli_parse.parse_option(item) for item in cli_args.load_options)
    if cli_args.source_representation:
        load_options["representation"] = cli_args.source_representation
    if cli_args.test:
        load_options["representation"] = "test_core"
    if cli_args.root_module:
        load_options["root_module"] = cli_args.root_module
    if cli_args.root_dir:
        load_options["root_dir"] = cli_args.root_dir

    save_options = dict(cli_parse.parse_option(item) for item in cli_args.save_options)
    if cli_args.destination_representation:
        save_options["representation"] = cli_args.destination_representation

    convert_options = {
        "save_options": save_options,
        "load_options": load_options,
        "inputs": cli_parse.parse_ewoks_inputs_parameters(cli_args),
    }
    if cli_args.exclude_requirements:
        convert_options["save_requirements"] = False
    cli_args.convert_options = convert_options
