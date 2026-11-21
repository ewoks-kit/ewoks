from typing import Any
from typing import Callable
from typing import Optional
from typing import Union

from ewoksutils.import_utils import qualname
from ewoksutils.task_utils import task_graph
from ewoksutils.task_utils import task_inputs

from .bindings import execute_graph


class TaskExecutor:
    def __init__(
        self,
        task: Union[str, type, Callable],
        task_type: Optional[str] = None,
        **execute_options,
    ) -> None:
        """Callable that executes a task and returns its result.

        .. code-block:: python

           sumfunc = TaskExecutor("mytasks.sumfunc")
           result = sumfunc(10, 20)

        :param task: Task identifier, task class or function.
        :param task_type: Task type. When not provided, it is guessed from the task.
        :param execute_options: Options for :func:`ewoks.execute_graph`.
        """
        if isinstance(task, str):
            task_identifier = task
        else:
            task_identifier = qualname(task)
            if task_type is None:
                task_type = "class" if isinstance(task, type) else "method"
        self._graph: dict = task_graph(task_identifier, task_type)
        self._execute_options: dict = execute_options

    @property
    def task_identifier(self) -> str:
        return self._graph["nodes"][0]["task_identifier"]

    @property
    def task_type(self) -> str:
        return self._graph["nodes"][0]["task_type"]

    def __call__(self, *args, **kwargs) -> Any:
        """Execute the task. Return the outputs, or the return value of a method task."""
        inputs = task_inputs(
            task_identifier=self.task_identifier,
            inputs={**dict(enumerate(args)), **kwargs},
        )
        result = execute_graph(
            self._graph,
            inputs=inputs,
            outputs=[{"all": True}],
            merge_outputs=True,
            **self._execute_options,
        )
        if self.task_type == "method":
            return result["return_value"]
        return result
