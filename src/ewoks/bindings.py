import importlib
from typing import Any, Optional, List, Union
from ewokscore.graph import TaskGraph


__all__ = ["execute_graph", "load_graph", "save_graph", "convert_graph"]


def import_binding(binding: Optional[str]):
    if not binding or binding.lower() == "none":
        binding = "ewokscore"
    elif not binding.startswith("ewoks"):
        binding = "ewoks" + binding
    return importlib.import_module(binding)


def execute_graph(
    graph,
    binding: Optional[str] = None,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    **execute_options
):
    if load_options is None:
        load_options = dict()
    graph = load_graph(graph, inputs=inputs, **load_options)
    mod = import_binding(binding)
    return mod.execute_graph(graph, **execute_options)


def load_graph(
    graph: Any, inputs: Optional[List[dict]] = None, **load_options
) -> TaskGraph:
    binding = _get_binding_for_format(graph, options=load_options)
    mod = import_binding(binding)
    return mod.load_graph(graph, inputs=inputs, **load_options)


def save_graph(graph: TaskGraph, destination, **save_options) -> Union[str, dict]:
    binding = _get_binding_for_format(destination, options=save_options)
    mod = import_binding(binding)
    return mod.save_graph(graph, destination, **save_options)


def convert_graph(
    source,
    destination,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    save_options: Optional[dict] = None,
) -> Union[str, dict]:
    if load_options is None:
        load_options = dict()
    if save_options is None:
        save_options = dict()
    graph = load_graph(source, inputs=inputs, **load_options)
    return save_graph(graph, destination, **save_options)


def _get_binding_for_format(graph, options: Optional[dict] = None) -> Optional[str]:
    """Get the binding which implements the workflow format (loading and saving)."""
    representation = None
    if options:
        representation = options.get("representation")
    if (
        representation is None
        and isinstance(graph, str)
        and graph.lower().endswith(".ows")
    ):
        representation = "ows"
    if representation == "ows":
        return "orange"
