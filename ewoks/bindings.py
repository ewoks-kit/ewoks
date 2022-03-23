import importlib
from typing import Optional, List


def import_binding(binding: Optional[str]):
    if not binding or binding.lower() == "none":
        binding = "ewokscore"
    elif not binding.startswith("ewoks"):
        binding = "ewoks" + binding
    return importlib.import_module(binding)


def as_ewoks_graph(graph, binding: Optional[str], **load_graph_options):
    if isinstance(graph, str) and graph.endswith(".ows") and binding != "orange":
        mod = importlib.import_module("ewoksorange.bindings")
        return mod.ows_to_ewoks(graph, **load_graph_options), True
    else:
        return graph, False


def execute_graph(
    graph,
    binding: Optional[str] = None,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    **execute_options
):
    if load_options is None:
        load_options = dict()
    graph, loaded = as_ewoks_graph(graph, binding, inputs=inputs, **load_options)
    if not loaded:
        execute_options["inputs"] = inputs
        execute_options["load_options"] = load_options
    mod = import_binding(binding)
    return mod.execute_graph(graph, **execute_options)
