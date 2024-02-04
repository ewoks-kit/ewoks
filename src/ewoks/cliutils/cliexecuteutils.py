from . import utils
from ewokscore.graph.serialize import GraphRepresentation

_REPRESENTATIONS = [str(s).split(".")[-1] for s in GraphRepresentation]


def add_execute_parameters(parser):
    parser.add_argument(
        "workflows",
        type=str,
        help="Workflow to execute (e.g. JSON filename)",
        nargs="+",
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
        "--workflow-format",
        type=str.lower,
        default="",
        dest="representation",
        choices=_REPRESENTATIONS,
        help="Source format",
    )
    parser.add_argument(
        "--data-root-uri",
        type=str,
        default="",
        dest="data_root_uri",
        help="Root for saving task results",
    )
    parser.add_argument(
        "--data-scheme",
        type=str,
        choices=["nexus", "json"],
        default="nexus",
        dest="data_scheme",
        help="Default task result format",
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
        "--option",
        dest="options",
        action="append",
        default=[],
        metavar="OPTION=VALUE",
        help="Execution options",
    )
    parser.add_argument(
        "-j",
        "--jobid",
        dest="job_id",
        type=str,
        default=None,
        help="Job id for ewoks events",
    )
    parser.add_argument(
        "--disable-events",
        action="store_true",
        help="Disable ewoks events",
    )
    parser.add_argument(
        "--sqlite3",
        dest="sqlite3_uri",
        type=str,
        default=None,
        help="Store ewoks events in an Sqlite3 database",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="The 'workflow' argument refers to the name of a test graph",
    )
    parser.add_argument(
        "--outputs",
        type=str,
        choices=["none", "end", "all"],
        default="none",
        help="Log outputs (per task or merged values dictionary)",
    )
    parser.add_argument(
        "--input-node-id",
        dest="node_attr",
        type=str,
        choices=["id", "label", "taskid"],
        default="id",
        help="The NODE attribute used when specifying an input parameter with [NODE:]NAME=VALUE",
    )
    parser.add_argument(
        "--inputs",
        type=str,
        choices=["start", "all"],
        default="start",
        help="Inputs without a specific node are given to either all start nodes or all nodes",
    )
    parser.add_argument(
        "--merge-outputs",
        action="store_true",
        dest="merge_outputs",
        help="Merge node outputs",
    )
    parser.add_argument(
        "--engine",
        type=str,
        choices=["none", "dask", "ppf", "orange"],
        default="none",
        help="Execution engine to be used",
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="The 'workflow' argument is a pattern to be search",
    )


def apply_execute_parameters(args):
    args.workflows, args.graphs = utils.parse_workflows(args)

    execute_options = dict(utils.parse_option(item) for item in args.options)

    execute_options["inputs"] = [
        utils.parse_parameter(input_item, args.node_attr, args.inputs == "all")
        for input_item in args.parameters
    ]

    if args.outputs == "all":
        execute_options["outputs"] = [{"all": True}]
    elif args.outputs == "end":
        execute_options["outputs"] = [{"all": False}]
    else:
        execute_options["outputs"] = []
    execute_options["merge_outputs"] = args.merge_outputs

    execute_options["varinfo"] = {
        "root_uri": args.data_root_uri,
        "scheme": args.data_scheme,
    }
    load_options = dict()
    execute_options["load_options"] = load_options
    if args.root_module:
        load_options["root_module"] = args.root_module
    if args.root_dir:
        load_options["root_dir"] = args.root_dir
    if args.representation:
        load_options["representation"] = args.representation

    execinfo = dict()
    execute_options["execinfo"] = execinfo
    if args.job_id:
        execinfo["job_id"] = args.job_id
    if args.sqlite3_uri:
        # TODO: asynchronous handling may loose events
        execinfo["asynchronous"] = False
        execinfo["handlers"] = [
            {
                "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
                "arguments": [{"name": "uri", "value": args.sqlite3_uri}],
            }
        ]

    args.execute_options = execute_options
