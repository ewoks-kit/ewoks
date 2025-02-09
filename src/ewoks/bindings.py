import logging
import os
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from ewokscore.events.contexts import RawExecInfoType
from ewokscore.events.contexts import job_context
from ewokscore.graph import TaskGraph
from ewokscore.graph.inputs import graph_inputs_as_table
from tabulate import tabulate

from . import _engines
from . import graph_cache
from .cliutils.utils import AbortException
from .cliutils.utils import pip_install
from .utils import extract_requirements
from .utils import save_current_env_as_requirements

try:
    from ewoksjob.client import submit
except ImportError:
    submit = None

try:
    from pyicat_plus.client import defaults as icat_defaults
    from pyicat_plus.client.main import IcatClient
except ImportError:
    IcatClient = None
    icat_defaults = None


__all__ = ["execute_graph", "load_graph", "save_graph", "convert_graph", "submit_graph"]

logger = logging.getLogger(__name__)


def execute_graph(
    graph,
    engine: Optional[str] = None,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    varinfo: Optional[dict] = None,
    execinfo: RawExecInfoType = None,
    task_options: Optional[dict] = None,
    outputs: Optional[List[dict]] = None,
    merge_outputs: Optional[bool] = True,
    environment: Optional[dict] = None,
    convert_destination: Optional[Any] = None,
    save_options: Optional[dict] = None,
    upload_parameters: Optional[dict] = None,
    **execute_options,
) -> Optional[dict]:
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
            convert_graph(graph, convert_destination, save_options=save_options)

        # Execute the graph
        engine_api = _engines.get_execution_engine(engine)
        result = engine_api.execute_graph(
            graph,
            varinfo=varinfo,
            execinfo=execinfo,
            task_options=task_options,
            outputs=outputs,
            merge_outputs=merge_outputs,
            **execute_options,
        )

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


def submit_graph(
    graph,
    _celery_options=None,
    resolve_graph_remotely: Optional[bool] = None,
    load_options: Optional[dict] = None,
    **options,
):
    """Submit a workflow to be executed remotely. The workflow is
    resolved on the client-side by default (e.g. load from a file)
    but can optionally be resolved remotely.
    """
    if submit is None:
        raise RuntimeError("requires the 'ewoksjob' package")
    if _celery_options is None:
        _celery_options = dict()
    if resolve_graph_remotely:
        options["load_options"] = load_options
    else:
        # Do not save requirements since the current env is the client
        graph = convert_graph(
            graph, None, load_options=load_options, save_requirements=False
        )
    return submit(args=(graph,), kwargs=options, **_celery_options)


@graph_cache.cache
def load_graph(
    graph: Any,
    inputs: Optional[List[dict]] = None,
    representation: Optional[str] = None,
    root_dir: Optional[Union[str, Path]] = None,
    root_module: Optional[str] = None,
    **load_options,
) -> TaskGraph:
    """When load option `graph_cache_max_size > 0` is provided, the graph will cached in memory.
    When the graph comes from external storage (for example a file) any changes
    to the external graph will require flushing the cache with `graph_cache_max_size = 0`.
    """
    engine_api, representation = _engines.get_serialization_engine(
        graph, representation=representation
    )
    return engine_api.deserialize_graph(
        graph,
        inputs=inputs,
        representation=representation,
        root_dir=root_dir,
        root_module=root_module,
        **load_options,
    )


def save_graph(
    graph: TaskGraph,
    destination,
    representation: Optional[str] = None,
    **save_options,
) -> Union[str, dict]:
    engine_api, representation = _engines.get_serialization_engine(
        destination, representation=representation
    )
    return engine_api.serialize_graph(
        graph, destination, representation=representation, **save_options
    )


def convert_graph(
    source,
    destination,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    save_options: Optional[dict] = None,
    save_requirements: bool = True,
) -> Union[str, dict]:
    if load_options is None:
        load_options = dict()
    if save_options is None:
        save_options = dict()
    graph = load_graph(source, inputs=inputs, **load_options)
    if save_requirements:
        graph = save_current_env_as_requirements(graph)
    return save_graph(graph, destination, **save_options)


def show_graph(
    source,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    original_source: Optional[str] = None,
    column_widths: Optional[Dict[str, Optional[int]]] = None,
) -> Union[str, dict]:
    if load_options is None:
        load_options = dict()
    graph = load_graph(source, inputs=inputs, **load_options)
    _print_graph(graph, column_widths=column_widths, original_source=original_source)


def _print_graph(
    graph: TaskGraph,
    column_widths: Optional[Dict[str, Optional[int]]] = None,
    original_source: Optional[str] = None,
) -> None:
    column_names, rows, metadata, footnotes = graph_inputs_as_table(
        graph, column_widths=column_widths
    )
    print()
    if original_source:
        print(f"Workflow: {original_source}")
    else:
        print("Workflow:")
    for key, value in metadata.items():
        label = key.replace("_", " ").capitalize()
        print(f"{label}: {value}")
    if rows:
        print(tabulate(rows, headers=column_names, tablefmt="fancy_grid"))
    else:
        print("No workflow inputs parameters detected!")
    for footnote in footnotes:
        print(footnote)


def install_graph(
    source,
    skip_prompt: bool = False,
    python_path: Optional[str] = None,
    load_options: Optional[dict] = None,
):
    if load_options is None:
        load_options = dict()
    graph = load_graph(source, **load_options)

    requirements = graph.requirements
    if requirements is None:
        logger.warning(
            "Requirements field is empty. Trying to extract requirements automatically..."
        )
        requirements = extract_requirements(graph)
        logger.info(f"Extracted the following requirements: {requirements}")

    if python_path is None:
        python_path = sys.executable

    if skip_prompt:
        pip_install(requirements, python_path)
        return

    requirements_as_str = "\n".join(requirements)

    answer = input(
        f"{requirements_as_str}\nThis will install the above packages via {python_path} -m pip install. Do you want to proceed (y/N)?"
    )
    if answer.lower() == "y" or answer.lower() == "yes":
        pip_install(requirements, python_path)
    else:
        raise AbortException()
