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
                f"Command of the package manager that will {action} the workflow "
                f"requirements. For example {examples}."
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
