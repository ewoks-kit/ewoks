from . import utils
from ewokscore.graph.serialize import GraphRepresentation

_REPRESENTATIONS = [str(s).split(".")[-1] for s in GraphRepresentation]


def add_convert_parameters(parser):
    parser.add_argument(
        "workflow",
        type=str,
        help="Workflow to convert (e.g. JSON filename)",
    )
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
        choices=_REPRESENTATIONS,
        help="Source format",
    )
    parser.add_argument(
        "--dst-format",
        type=str.lower,
        default="",
        dest="destination_representation",
        choices=_REPRESENTATIONS,
        help="Destination format",
    )
    parser.add_argument(
        "--workflow-dir",
        type=str,
        default="",
        dest="root_dir",
        help="Directory of sub-workflows (current working directory by default)",
    )
    parser.add_argument(
        "--workflow-module",
        type=str,
        default="",
        dest="root_module",
        help="Python module of sub-workflows (current working directory by default)",
    )
    parser.add_argument(
        "-p",
        "--parameter",
        dest="parameters",
        action="append",
        default=[],
        metavar="[NODE:]NAME=VALUE",
        help="Input variable for a particular node (or all start nodes when missing)",
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
        "--test",
        action="store_true",
        help="The 'workflow' argument refers to the name of a test graph",
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="The 'workflow' argument is a pattern to be search",
    )


def apply_convert_parameters(args):
    args.workflows, args.graphs = utils.parse_workflow(args)
    args.destinations = utils.parse_destinations(args)

    inputs = [
        utils.parse_parameter(input_item, "id", False) for input_item in args.parameters
    ]

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
        "inputs": inputs,
    }
    args.convert_options = convert_options
