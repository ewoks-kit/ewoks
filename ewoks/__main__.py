import sys
import logging
import importlib
from pprint import pformat
from typing import Optional
from ewokscore import cliutils

logger = logging.getLogger(__name__)


def import_binding(binding: str):
    if binding == "none":
        binding = "ewokscore"
    else:
        binding = "ewoks" + binding
    return importlib.import_module(binding)


def parse_input(input_item: str):
    node_and_name, _, value = input_item.partition("=")
    label, _, name = node_and_name.partition(":")
    if value.isdigit():
        if value.isdecimal():
            value = int(value)
        else:
            value = float(value)
    if name:
        return {"label": label, "name": name, "value": value}
    else:
        return {"name": label, "value": value}  # all input nodes


def execute_workflow(args) -> Optional[dict]:
    if args.test:
        from ewokscore.tests.examples.graphs import graph_names, get_graph

        graphs = list(graph_names())
        if args.workflow not in graphs:
            logger.error("Test graph '%s' does not exist: %s", args.workflow, graphs)
            return None

        graph, _ = get_graph(args.workflow)
    else:
        graph = args.workflow

    inputs = [parse_input(input_item) for input_item in args.parameters]

    results_of_all_nodes = args.output == "all"
    outputs = None
    if args.output == "all_values":
        outputs = [{"all": True}]
    elif args.output == "end_values":
        outputs = [{"all": False}]

    binding = import_binding(args.scheduler)
    execute_graph = getattr(binding, "execute_graph")

    varinfo = {"root_uri": args.root_uri, "scheme": args.scheme}
    results = execute_graph(
        graph,
        varinfo=varinfo,
        inputs=inputs,
        outputs=outputs,
        results_of_all_nodes=results_of_all_nodes,
    )
    logger.info("Results for workflow '%s': \n%s", args.workflow, pformat(results))
    return results


def main(argv=None, shell=True):
    import argparse

    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description="Esrf WOrKflow Sytem CLI", prog="ewoks"
    )

    subparsers = parser.add_subparsers(help="Commands", dest="command")
    execute = subparsers.add_parser("execute", help="Execute a workflow")

    execute.add_argument(
        "workflow",
        type=str,
        help="URI to a workflow (e.g. JSON filename)",
    )
    execute.add_argument(
        "--scheduler",
        type=str,
        choices=["none", "dask", "ppf", "orange"],
        default="none",
        help="Task scheduler to be used",
    )
    execute.add_argument(
        "--root_uri",
        type=str,
        default="",
        help="Root for saving task results",
    )
    execute.add_argument(
        "--scheme",
        type=str,
        choices=["nexus", "json"],
        default="nexus",
        help="Default task result format",
    )
    execute.add_argument(
        "-p",
        "--parameter",
        dest="parameters",
        action="append",
        default=[],
        metavar="[NODE:]NAME=VALUE",
        help="Input variable for a particular node (or all start nodes when missing)",
    )
    execute.add_argument(
        "--test",
        action="store_true",
        help="The workflow arguments is the name of a test graph",
    )
    execute.add_argument(
        "--output",
        type=str,
        choices=["end", "all", "end_values", "all_values"],
        default="end",
        help="Log outputs (per task or merged values dictionary)",
    )

    if shell:
        cliutils.add_log_parameters(parser)
    args, _ = parser.parse_known_args(argv[1:])
    if shell:
        cliutils.apply_log_parameters(args)

    if args.command == "execute":
        results = execute_workflow(args)
        if shell:
            if results is None:
                return 1
            else:
                return 0
        else:
            return results

    if shell:
        return 0
    else:
        return None


if __name__ == "__main__":
    sys.exit(main())
