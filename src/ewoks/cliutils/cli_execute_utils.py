from .._engines import get_engine_names
from .._engines import get_graph_representations
from . import utils


def add_execute_parameters(parser):
    utils.add_common_parameters(parser, "execute")
    utils.add_subworkflows_parameters(parser)
    utils.add_ewoks_inputs_parameters(parser)

    parser.add_argument(
        "--workflow-format",
        type=str.lower,
        default="",
        dest="representation",
        choices=get_graph_representations(),
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
        "-o",
        "--option",
        dest="options",
        action="append",
        default=[],
        metavar="OPTION=VALUE",
        help="Execution option",
    )
    parser.add_argument(
        "-t",
        "--task-option",
        dest="task_options",
        action="append",
        default=[],
        metavar="OPTION=VALUE",
        help="Ewoks task option",
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
        "--outputs",
        type=str,
        choices=["none", "end", "all"],
        default="none",
        help="Log outputs (per task or merged values dictionary)",
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
        choices=get_engine_names(),
        default="core",
        help="Execution engine to be used",
    )


def apply_execute_parameters(args):
    args.workflows, args.graphs = utils.parse_workflows(args)

    inputs = [
        utils.parse_parameter(input_item, args.node_attr, args.inputs == "all")
        for input_item in args.parameters
    ]

    if args.outputs == "all":
        outputs = [{"all": True}]
    elif args.outputs == "end":
        outputs = [{"all": False}]
    else:
        outputs = []

    varinfo = {
        "root_uri": args.data_root_uri,
        "scheme": args.data_scheme,
    }

    load_options = dict()
    if args.root_module:
        load_options["root_module"] = args.root_module
    if args.root_dir:
        load_options["root_dir"] = args.root_dir
    if args.representation:
        load_options["representation"] = args.representation

    execinfo = dict()
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

    task_options = dict(utils.parse_option(item) for item in args.task_options)

    execute_options = dict(utils.parse_option(item) for item in args.options)
    execute_options["inputs"] = inputs
    execute_options["outputs"] = outputs
    execute_options["merge_outputs"] = args.merge_outputs
    execute_options["load_options"] = load_options
    execute_options["varinfo"] = varinfo
    execute_options["execinfo"] = execinfo
    execute_options["task_options"] = task_options

    args.execute_options = execute_options
