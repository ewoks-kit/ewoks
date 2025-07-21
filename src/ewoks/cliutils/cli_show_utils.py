from .._engines import get_graph_representations
from . import utils


def add_show_parameters(parser):
    utils.add_common_parameters(parser, "show")
    utils.add_subworkflows_parameters(parser)
    utils.add_ewoks_inputs_parameters(parser)

    parser.add_argument(
        "--src-format",
        type=str.lower,
        default="",
        dest="source_representation",
        choices=get_graph_representations(),
        help="Source format",
    )
    parser.add_argument(
        "-o",
        "--load-option",
        dest="load_options",
        action="append",
        default=[],
        metavar="OPTION=VALUE",
        help="Load options",
    )


def apply_show_parameters(args):
    args.workflows, args.graphs = utils.parse_workflows(args)

    load_options = dict(utils.parse_option(item) for item in args.load_options)
    if args.source_representation:
        load_options["representation"] = args.source_representation
    if args.root_module:
        load_options["root_module"] = args.root_module
    if args.root_dir:
        load_options["root_dir"] = args.root_dir

    show_options = {
        "load_options": load_options,
        "inputs": utils.parse_ewoks_inputs_parameters(args),
    }
    args.show_options = show_options
