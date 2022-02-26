import os
import importlib
import tempfile
from typing import Optional, List
from contextlib import contextmanager


def import_binding(binding: Optional[str]):
    if not binding or binding.lower() == "none":
        binding = "ewokscore"
    elif not binding.startswith("ewoks"):
        binding = "ewoks" + binding
    return importlib.import_module(binding)


@contextmanager
def convert_to_ewoks_graph(graph, binding: Optional[str], **load_graph_options):
    if isinstance(graph, str) and graph.endswith(".ows") and binding != "orange":
        mod = importlib.import_module("ewoksorange.bindings")
        with tempfile.TemporaryDirectory(prefix="ewoks") as tmpdirname:
            filename = os.path.join(tmpdirname, "ewokstaskgraph.json")
            yield mod.ows_to_ewoks(graph, filename, **load_graph_options)
    else:
        yield graph


def execute_graph(
    graph,
    binding: Optional[str] = None,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    **execute_options
):
    with convert_to_ewoks_graph(
        graph, binding, inputs=inputs, load_options=load_options
    ) as graph:
        mod = import_binding(binding)
        return mod.execute_graph(
            graph, inputs=inputs, load_options=load_options, **execute_options
        )
