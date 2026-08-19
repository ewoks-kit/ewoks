from typing import List

from ewoksutils.cli_utils.cli_arguments import CLIArg

from .._engines import get_graph_representations
from .._requirements import supported_managers


def package_manager_arguments(action: str) -> List[CLIArg]:
    """CLI arguments to select the package manager that will `action` requirements."""
    examples = ", ".join(
        f'"{command}" for {name}' for name, command in supported_managers().items()
    )
    return [
        CLIArg(
            "package_manager_name",
            ["--package-manager-name"],
            type=str.lower,
            choices=list(supported_managers()),
            help=f"Package manager to {action} the workflow requirements.",
        ),
        CLIArg(
            "package_manager_command",
            ["--package-manager-command"],
            type=str,
            help=(
                f"Command that invokes the package manager which will {action} the "
                f"workflow requirements. For example {examples}."
            ),
        ),
    ]


def environment_arguments() -> List[CLIArg]:
    """CLI arguments to select the python environment that runs the command."""
    return [
        CLIArg(
            "env",
            ["--env"],
            type=str,
            help=(
                "Location of the python environment in which to run, for example "
                "created by 'ewoks install'. Default: the current environment."
            ),
        ),
    ]


def ewoks_load_arguments() -> List[CLIArg]:
    return [
        CLIArg(
            "source_representation",
            ["--src-format"],
            type=str.lower,
            choices=get_graph_representations(),
            help="Source format.",
        ),
        CLIArg(
            "load_options",
            ["-o", "--load-option"],
            action="append",
            metavar="OPTION=VALUE",
            help="Load options.",
        ),
    ]
