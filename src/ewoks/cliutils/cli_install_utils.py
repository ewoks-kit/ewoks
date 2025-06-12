from argparse import ArgumentParser

from . import utils


def add_install_parameters(parser: ArgumentParser):
    utils.add_common_parameters(parser, "install")
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
