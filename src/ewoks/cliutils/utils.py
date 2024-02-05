import os
import json
from glob import glob
from fnmatch import fnmatch
from typing import Tuple, Any, List
from json.decoder import JSONDecodeError


def parse_value(value: str) -> Any:
    try:
        return json.loads(value)
    except JSONDecodeError:
        return value


_NODE_ATTR_MAP = {"id": "id", "label": "label", "taskid": "task_identifier"}


def parse_parameter(input_item: str, node_attr: str, all: bool) -> dict:
    """The format of `input_item` is `"[NODE]:name=value"`"""
    node_and_name, _, value = input_item.partition("=")
    a, sep, b = node_and_name.partition(":")
    if sep:
        node = a
        var_name = b
    else:
        node = None
        var_name = a
    var_value = parse_value(value)
    if node is None:
        return {"all": all, "name": var_name, "value": var_value}
    return {
        _NODE_ATTR_MAP[node_attr]: node,
        "name": var_name,
        "value": var_value,
    }


def parse_option(option: str) -> Tuple[str, Any]:
    option, _, value = option.partition("=")
    return option, parse_value(value)


def parse_workflow(args) -> Tuple[List[str], List[str]]:
    """
    :returns: workflows (possibly expanded due the search), graphs (execute graph arguments)
    """
    if args.test:
        return _parse_test_workflows([args.workflow], args.search)
    return _parse_workflows([args.workflow], args.search)


def parse_workflows(args) -> Tuple[List[str], List[str]]:
    """
    :returns: workflows (possibly expanded due the search), graphs (execute graph arguments)
    """
    if args.test:
        return _parse_test_workflows(args.workflows, args.search)
    return _parse_workflows(args.workflows, args.search)


def _parse_workflows(workflows: List[str], search: bool) -> Tuple[List[str], List[str]]:
    """
    :returns: workflows (possibly expanded due the search), graphs (execute graph arguments)
    """
    if not search:
        return workflows, workflows
    parsed_workflows = list()
    for workflow in workflows:
        for filename in glob(workflow):
            if filename not in parsed_workflows:
                parsed_workflows.append(filename)
    return parsed_workflows, parsed_workflows


def _parse_test_workflows(
    workflows: List[str], search: bool
) -> Tuple[List[str], List[dict]]:
    """
    :returns: workflows (possibly expanded due the search), graphs (execute graph arguments)
    """
    from ewokscore.tests.examples.graphs import graph_names, get_graph

    test_workflows = list(graph_names())
    if search:
        parsed_workflows = list()
        for workflow in workflows:
            for test_graph in test_workflows:
                if fnmatch(test_graph, workflow) and test_graph not in parsed_workflows:
                    parsed_workflows.append(test_graph)
    else:
        for workflow in workflows:
            if workflow not in test_workflows:
                raise RuntimeError(
                    f"Test graph '{workflow}' does not exist: {test_workflows}"
                )
        parsed_workflows = workflows

    graphs = [get_graph(workflow)[0] for workflow in parsed_workflows]
    return parsed_workflows, graphs


def parse_destinations(args):
    dest_dirname = os.path.dirname(args.destination)
    basename = os.path.basename(args.destination)
    dest_basename, dest_ext = os.path.splitext(basename)
    if not dest_ext:
        dest_ext = dest_basename
        dest_basename = ""
        if not dest_ext.startswith("."):
            dest_ext = f".{dest_ext}"

    if len(args.workflows) == 1 and dest_basename:
        return [os.path.join(dest_dirname, f"{dest_basename}{dest_ext}")]

    destinations = list()
    for workflow in args.workflows:
        basename, _ = os.path.splitext(os.path.basename(workflow))
        destination = os.path.join(dest_dirname, f"{basename}{dest_basename}{dest_ext}")
        destinations.append(destination)

    return destinations
