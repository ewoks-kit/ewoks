import json
from typing import Tuple, Any


def parse_value(value: str) -> Any:
    try:
        return json.loads(value)
    except Exception:
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


def parse_workflow(args):
    if args.test:
        from ewokscore.tests.examples.graphs import graph_names, get_graph

        graphs = list(graph_names())
        if args.workflow not in graphs:
            raise RuntimeError(f"Test graph '{args.workflow}' does not exist: {graphs}")

        graph, _ = get_graph(args.workflow)
    else:
        graph = args.workflow
    return graph
