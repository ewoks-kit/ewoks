from argparse import ArgumentParser
from . import utils


def add_install_parameters(parser: ArgumentParser):
    parser.add_argument(
        "workflows",
        type=str,
        help="Workflows to install (e.g. JSON filename)",
        nargs="+",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="The 'workflows' argument refers to the name of a test graph",
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="The 'workflows' argument is a pattern to be searched",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Accept automatically install prompts",
    )
    parser.add_argument(
        "-p",
        "--python",
        type=str,
        help="Python of the env where the packages should be installed. Default: current env Python.",
    )


def apply_install_parameters(args):
    args.workflows, args.graphs = utils.parse_workflows(args)
