import logging
from argparse import Namespace
from typing import List

from ewoksutils.cli_utils import cli_arguments
from ewoksutils.cli_utils import cli_log_utils
from ewoksutils.cli_utils import cli_parse
from ewoksutils.cli_utils.cli_spec import CLIArg

from .._requirements import managers_supporting_in_place
from .._requirements.utils.base_manager import EWOKS_ENVIRONMENTS_ROOT
from .cli_arguments import package_manager_arguments

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
            "env_name",
            ["--env-name"],
            type=str,
            help=(
                "Name of the python environment to create. Default: the workflow "
                "identifier."
            ),
        ),
        CLIArg(
            "env_root",
            ["--env-root"],
            type=str,
            help=(
                "Directory in which the python environment is created. Default: the "
                "directory in which the package manager creates environments "
                f"('{EWOKS_ENVIRONMENTS_ROOT}' for package managers that do not have "
                "one)."
            ),
        ),
        CLIArg(
            "clean",
            ["--clean"],
            action="store_true",
            help=(
                "Remove the python environment when it already exists instead of "
                "installing in it."
            ),
        ),
        CLIArg(
            "in_place",
            ["--in-place"],
            action="store_true",
            help=(
                "Install in the current python environment instead of creating one "
                f"(only {', '.join(managers_supporting_in_place())})."
            ),
        ),
        CLIArg(
            "python_version",
            ["--python-version"],
            type=str,
            help=(
                "Python version of the environment to create. Default: the python "
                "version of the workflow requirements."
            ),
        ),
        CLIArg(
            "with_ewoks",
            ["--with-ewoks"],
            action="store_true",
            help=(
                "Add ewoks to the environment when the requirements do not contain "
                "it, so the workflow can be executed in the environment."
            ),
        ),
    ]
    args_list += package_manager_arguments("install")
    return args_list


def parse_install_arguments(cli_args: Namespace, shell: bool = False) -> None:
    if shell:
        cli_log_utils.parse_log_arguments(cli_args)
    cli_args.workflows, cli_args.graphs = cli_parse.parse_workflows(cli_args)
    if cli_args.env_name and len(cli_args.workflows) > 1:
        raise ValueError("'--env-name' requires a single workflow")
    if cli_args.in_place and (cli_args.env_name or cli_args.env_root or cli_args.clean):
        raise ValueError(
            "'--in-place' cannot be combined with '--env-name', '--env-root' or "
            "'--clean'"
        )
