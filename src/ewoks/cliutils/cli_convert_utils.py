from .._engines import get_graph_representations
from . import utils


def add_convert_parameters(parser):
    utils.add_common_parameters(parser, "convert")
    utils.add_subworkflows_parameters(parser)
    utils.add_ewoks_inputs_parameters(parser)

    parser.add_argument(
        "destination",
        type=str,
        help="Destination of the conversion (e.g. JSON filename)",
    )
    parser.add_argument(
        "--src-format",
        type=str.lower,
        default="",
        dest="source_representation",
        choices=get_graph_representations(),
        help="Source format",
    )
    parser.add_argument(
        "--dst-format",
        type=str.lower,
        default="",
        dest="destination_representation",
        choices=get_graph_representations(),
        help="Destination format",
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
    parser.add_argument(
        "-s",
        "--save-option",
        dest="save_options",
        action="append",
        default=[],
        metavar="OPTION=VALUE",
        help="Save options",
    )
    parser.add_argument(
        "--exclude-requirements",
        dest="exclude_requirements",
        action="store_true",
        help="Do not include the packages of the current Python env as requirements in the destination workflow",
    )


def apply_convert_parameters(args):
    args.workflows, args.graphs = utils.parse_workflows(args)
    args.destinations = utils.parse_destinations(args)

    load_options = dict(utils.parse_option(item) for item in args.load_options)
    if args.source_representation:
        load_options["representation"] = args.source_representation
    if args.root_module:
        load_options["root_module"] = args.root_module
    if args.root_dir:
        load_options["root_dir"] = args.root_dir

    save_options = dict(utils.parse_option(item) for item in args.save_options)
    if args.destination_representation:
        save_options["representation"] = args.destination_representation

    convert_options = {
        "save_options": save_options,
        "load_options": load_options,
        "inputs": utils.parse_ewoks_inputs_parameters(args),
    }
    if args.exclude_requirements:
        convert_options["save_requirements"] = False
    args.convert_options = convert_options
