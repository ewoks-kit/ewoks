from argparse import Namespace
from typing import List

from ewoksutils.cli_utils import cli_arguments
from ewoksutils.cli_utils import cli_log_utils
from ewoksutils.cli_utils import cli_parse
from ewoksutils.cli_utils.cli_spec import CLIArg

from .cli_arguments import ewoks_load_arguments


def show_arguments(
    shell: bool = False, default_log_level: str = "warning"
) -> List[CLIArg]:
    if shell:
        args_list = cli_log_utils.log_arguments(default_log_level=default_log_level)
    else:
        args_list = []

    args_list += cli_arguments.workflow_arguments("show")
    args_list += cli_arguments.ewoks_inputs_arguments()
    args_list += ewoks_load_arguments()
    return args_list


def parse_show_arguments(cli_args: Namespace, shell: bool = False) -> None:
    if shell:
        cli_log_utils.parse_log_arguments(cli_args)
    cli_args.workflows, cli_args.graphs = cli_parse.parse_workflows(cli_args)

    load_options = dict(cli_parse.parse_option(item) for item in cli_args.load_options)
    if cli_args.source_representation:
        load_options["representation"] = cli_args.source_representation
    if cli_args.root_module:
        load_options["root_module"] = cli_args.root_module
    if cli_args.root_dir:
        load_options["root_dir"] = cli_args.root_dir
    if cli_args.test:
        load_options["representation"] = "test_core"

    show_options = {
        "load_options": load_options,
        "inputs": cli_parse.parse_ewoks_inputs_parameters(cli_args),
    }
    cli_args.show_options = show_options
