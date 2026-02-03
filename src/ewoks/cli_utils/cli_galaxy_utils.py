from argparse import Namespace
from typing import Any
from typing import List
from typing import Tuple

from ewoksutils.cli_utils import cli_log_utils
from ewoksutils.cli_utils.cli_parse import parse_value
from ewoksutils.cli_utils.cli_spec import CLIArg


def galaxy_arguments(
    shell: bool = False, default_log_level: str = "warning"
) -> List[CLIArg]:
    if shell:
        args_list = cli_log_utils.log_arguments(default_log_level=default_log_level)
    else:
        args_list = []

    args_list.append(
        CLIArg(
            dest="task_qualifier_name",
            flags=[],
            help="Full task qualifier name to execute",
        )
    )
    args_list.append(
        CLIArg(
            "parameters",
            ["-p", "--parameter"],
            help="Input for the task",
            action="append",
            metavar="NAME=VALUE",
        ),
    )

    return args_list


def parse_parameter(parameter: str) -> Tuple[str, Any]:
    name, _, value = parameter.partition("=")

    return name, parse_value(value)


def parse_galaxy_arguments(cli_args: Namespace, shell: bool = False):
    if shell:
        cli_log_utils.parse_log_arguments(cli_args)

    parsed_parameters = {}
    for parameter in cli_args.parameters:
        name, value = parse_parameter(parameter)
        parsed_parameters[name] = value
    cli_args.parameters = parsed_parameters
