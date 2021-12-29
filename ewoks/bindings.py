import importlib
from typing import Optional


def import_binding(binding: Optional[str]):
    if not binding or binding.lower() == "none":
        binding = "ewokscore"
    elif not binding.startswith("ewoks"):
        binding = "ewoks" + binding
    return importlib.import_module(binding)


def execute_graph(graph, binding=None, **kwargs):
    binding = import_binding(binding)
    execute_graph = getattr(binding, "execute_graph")
    return execute_graph(graph, **kwargs)
