import logging
from argparse import Namespace
from typing import List

from ewoksutils.cli_utils import cli_arguments
from ewoksutils.cli_utils import cli_log_utils
from ewoksutils.cli_utils import cli_parse
from ewoksutils.cli_utils.cli_spec import CLIArg

logger = logging.getLogger(__name__)


def install_arguments(
    shell: bool = False, default_log_level: str = "info"
) -> List[CLIArg]:
    if shell:
        args_list = cli_log_utils.log_arguments(default_log_level=default_log_level)
    else:
        args_list = []

    args_list += cli_arguments.workflow_arguments("install")
    args_list += [
        CLIArg(
            "yes",
            ["--yes"],
            action="store_true",
            help="Automatically accept installation prompts.",
        ),
        CLIArg(
            "python",
            ["-p", "--python"],
            type=str,
            help="Python interpreter of the environment where the packages should be installed. Default: current environment Python.",
        ),
    ]
    return args_list


def parse_install_arguments(cli_args: Namespace, shell: bool = False) -> None:
    if shell:
        cli_log_utils.parse_log_arguments(cli_args)
    cli_args.workflows, cli_args.graphs = cli_parse.parse_workflows(cli_args)
