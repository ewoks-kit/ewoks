from collections.abc import Mapping
from typing import List, Optional, Union
from ewokscore import Task
from ewoksutils.import_utils import qualname

try:
    from ewoksjob.client import submit
except ImportError:
    submit = None

from .bindings import execute_graph, load_graph

__all__ = ["task_inputs", "execute_task", "submit_task"]


def task_inputs(
    id: Optional[str] = None,
    label: Optional[str] = None,
    task_identifier: Optional[str] = None,
    inputs: Optional[Mapping] = None,
) -> List[dict]:
    """Convert a {name: value} dict of inputs to a list of workflow inputs for given tasks.

    Provide one of ``id``, ``label`` and ``task_identifier`` to select the targeted tasks.

    .. code:: python

       inputs = task_inputs(task_identifier="SumTask", inputs={"a": 1, "b": 1})

    """
    if inputs is None:
        return []

    task_selector = {}
    if id is not None:
        task_selector["id"] = id
    if label is not None:
        task_selector["label"] = label
    if task_identifier is not None:
        task_selector["task_identifier"] = task_identifier

    return [{**task_selector, "name": k, "value": v} for k, v in inputs.items()]


def _task_graph(
    task_identifier: str,
    task_type: str,
):
    return {
        "graph": {"id": task_identifier},
        "nodes": [
            {
                "id": task_identifier,
                "task_type": task_type,
                "task_identifier": task_identifier,
            },
        ],
        "links": [],
    }


def _convert_inputs(
    task_identifier: str,
    inputs: Optional[Union[Mapping, List[Mapping]]],
):
    if inputs is None:
        return []
    if isinstance(inputs, Mapping):
        return task_inputs(task_identifier=task_identifier, inputs=inputs)
    return inputs


def execute_task(
    task: Union[str, Task],
    inputs: Optional[Union[Mapping, List[Mapping]]] = None,
    task_type: str = "class",
    **options,
):
    """Execute a workflow with a unique task and return its output.

    :param task: Task identifier or Task class
    :param inputs:
        Task inputs as a {name: value} mapping or a list of workflow inputs
    :param task_type: The kind of task
    :param options: Options passed to :func:`ewoks.bindings.execute_graph`
    """
    task_identifier = task if isinstance(task, str) else qualname(task)

    return execute_graph(
        _task_graph(task_identifier, task_type),
        inputs=_convert_inputs(task_identifier, inputs),
        **options,
    )


def submit_task(
    task_identifier: str,
    inputs: Optional[Union[Mapping, List[Mapping]]] = None,
    task_type: str = "class",
    _celery_options=None,
    **options,
):
    """Submit a workflow containing a unique task to be executed remotely.

    :param task: Task identifier
    :param inputs:
        Task inputs as a {name: value} mapping or a list of workflow inputs
    :param task_type: The kind of task
    :param _celery_options: Option passed to :func:`ewoksjob.client.submit`
    :param options: Options passed as kwargs to :func:`ewoksjob.client.submit`
    """
    if submit is None:
        raise RuntimeError("requires the 'ewoksjob' package")
    if _celery_options is None:
        _celery_options = dict()

    graph = load_graph(
        graph=_task_graph(task_identifier, task_type),
        inputs=_convert_inputs(task_identifier, inputs),
    ).serialize()
    print(graph)

    return submit(args=(graph,), kwargs=options, **_celery_options)
