import os
import importlib
from warnings import warn
from typing import Any, Optional, List, Union
from ewokscore.graph import TaskGraph
from ewokscore.events.contexts import job_context, RawExecInfoType


try:
    from ewoksjob.client import submit
except ImportError:
    submit = None


__all__ = ["execute_graph", "load_graph", "save_graph", "convert_graph", "submit_graph"]


def import_binding(engine: Optional[str]):
    if not engine or engine.lower() == "none":
        binding = "ewokscore"
    elif engine.startswith("ewoks"):
        warn(
            f"engine = '{engine}' is deprecated in favor of '{engine[5:]}'",
            FutureWarning,
        )
        binding = engine
    else:
        binding = "ewoks" + engine
    return importlib.import_module(binding)


def execute_graph(
    graph,
    engine: Optional[str] = None,
    binding: Optional[str] = None,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    execinfo: RawExecInfoType = None,
    environment: Optional[dict] = None,
    **execute_options,
):
    if binding:
        if engine:
            raise ValueError("'binding' and 'engine' cannot be used together")
        engine = binding
        warn("'binding' is deprecated in favor of 'engine'", FutureWarning)
    with job_context(execinfo, engine=engine) as execinfo:
        if load_options is None:
            load_options = dict()
        if environment:
            environment = {k: str(v) for k, v in environment.items()}
            os.environ.update(environment)
        graph = load_graph(graph, inputs=inputs, **load_options)
        mod = import_binding(engine)
        return mod.execute_graph(graph, execinfo=execinfo, **execute_options)


def submit_graph(graph, **options):
    if submit is None:
        raise RuntimeError("requires the 'ewoksjob' package")
    return submit(args=(graph,), kwargs=options)


def load_graph(
    graph: Any, inputs: Optional[List[dict]] = None, **load_options
) -> TaskGraph:
    engine = _get_engine_for_format(graph, options=load_options)
    mod = import_binding(engine)
    return mod.load_graph(graph, inputs=inputs, **load_options)


def save_graph(graph: TaskGraph, destination, **save_options) -> Union[str, dict]:
    engine = _get_engine_for_format(destination, options=save_options)
    mod = import_binding(engine)
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


def _get_engine_for_format(graph, options: Optional[dict] = None) -> Optional[str]:
    """Get the engine which implements the workflow format (loading and saving)."""
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
