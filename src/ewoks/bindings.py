import os
import logging
import importlib
from warnings import warn
from typing import Any, Optional, List, Union
from ewokscore.graph import TaskGraph
from ewokscore.events.contexts import job_context, RawExecInfoType
from . import graph_cache

try:
    from ewoksjob.client import submit
except ImportError:
    submit = None

try:
    from pyicat_plus.client.main import IcatClient
    from pyicat_plus.client import defaults as icat_defaults
except ImportError:
    IcatClient = None
    icat_defaults = None


__all__ = ["execute_graph", "load_graph", "save_graph", "convert_graph", "submit_graph"]

logger = logging.getLogger(__name__)


def import_binding(engine: Optional[str]):
    if not engine or engine.lower() == "none":
        binding = "ewokscore"
    elif engine.startswith("ewoks"):
        warn(
            f"engine = '{engine}' is deprecated in favor of '{engine[5:]}'",
            DeprecationWarning,
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
    convert_destination: Optional[Any] = None,
    save_options: Optional[dict] = None,
    upload_parameters: Optional[dict] = None,
    **execute_options,
):
    if binding:
        if engine:
            raise ValueError("'binding' and 'engine' cannot be used together")
        engine = binding
        warn("'binding' is deprecated in favor of 'engine'", DeprecationWarning)
    with job_context(execinfo, engine=engine) as execinfo:
        if environment:
            environment = {k: str(v) for k, v in environment.items()}
            os.environ.update(environment)

        # Load the graph
        if load_options is None:
            load_options = dict()
        graph = load_graph(graph, inputs=inputs, **load_options)

        # Save the graph (with inputs)
        if convert_destination is not None:
            if save_options is None:
                save_options = dict()
            save_graph(graph, convert_destination, **save_options)

        # Execute the graph
        mod = import_binding(engine)
        result = mod.execute_graph(graph, execinfo=execinfo, **execute_options)

        # Upload results
        if upload_parameters:
            _upload_result(upload_parameters)
        return result


def _upload_result(upload_parameters):
    if IcatClient is None:
        raise RuntimeError("requires pyicat-plus")
    metadata_urls = upload_parameters.pop(
        "metadata_urls", icat_defaults.METADATA_BROKERS
    )
    client = IcatClient(metadata_urls=metadata_urls)
    logger.info(
        "Sending processed dataset '%s' to ICAT: %s",
        upload_parameters.get("dataset"),
        upload_parameters.get("path"),
    )
    client.store_processed_data(**upload_parameters)


def submit_graph(graph, _celery_options=None, **options):
    if submit is None:
        raise RuntimeError("requires the 'ewoksjob' package")
    if _celery_options is None:
        _celery_options = dict()
    return submit(args=(graph,), kwargs=options, **_celery_options)


@graph_cache.cache
def load_graph(
    graph: Any, inputs: Optional[List[dict]] = None, **load_options
) -> TaskGraph:
    """When load option `graph_cache_max_size > 0` is provided, the graph will cached in memory.
    When the graph comes from external storage (for example a file) any changes
    to the external graph will require flushing the cache with `graph_cache_max_size = 0`.
    """
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
