from typing import List

from ewoksutils.cli_utils.cli_arguments import CLIArg

from .._engines import get_graph_representations


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
