import datetime
import logging
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Generator
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
from ._requirements.pip.extract import add_current_env_pip_requirements
from ._requirements.pip.extract import extract_pip_requirements
from ._requirements.pip.install import pip_install
from .errors import AbortException

try:
    from ewoksjob.bindings import submit_graph as _submit_graph
    from ewoksjob.client.futures import FutureInterface
except ImportError:
    _submit_graph = None
    FutureInterface = Any

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
        with _upload_context(upload_parameters):
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

            return result


@contextmanager
def _upload_context(upload_parameters: Optional[dict]) -> Generator[None, None, None]:
    if upload_parameters is None:
        yield
        return

    if IcatClient is None:
        raise RuntimeError("requires the 'pyicat-plus' package")

    metadata = upload_parameters.setdefault("metadata", {})
    if "startDate" not in metadata:
        metadata["startDate"] = datetime.datetime.now().astimezone()

    yield

    # Only upload when no exception is raised.

    if "endDate" not in metadata:
        metadata["endDate"] = datetime.datetime.now().astimezone()

    metadata_urls = upload_parameters.pop(
        "metadata_urls", icat_defaults.METADATA_BROKERS
    )
    client = IcatClient(metadata_urls=metadata_urls)
    logger.info(
        "Upload processed dataset '%s' metadata to ICAT: %s",
        upload_parameters.get("dataset"),
        upload_parameters.get("path"),
    )
    client.store_processed_data(**upload_parameters)


def submit_graph(
    graph,
    _celery_options: Optional[dict] = None,
    resolve_graph_remotely: Optional[bool] = None,
    load_options: Optional[dict] = None,
    **options,
) -> FutureInterface:
    """Submit a workflow to be executed remotely. The workflow is
    resolved on the client-side by default (e.g. load from a file)
    but can optionally be resolved remotely.
    """
    if _submit_graph is None:
        raise RuntimeError("requires the 'ewoksjob' package")
    return _submit_graph(
        graph,
        _convert_graph=_load_graph,
        _celery_options=_celery_options,
        resolve_graph_remotely=resolve_graph_remotely,
        load_options=load_options,
        **options,
    )


def _load_graph(graph, load_options: Optional[dict] = None) -> dict:
    return convert_graph(
        graph, None, load_options=load_options, save_requirements=False
    )


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
        graph = add_current_env_pip_requirements(graph)
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
        requirements = extract_pip_requirements(graph)
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
