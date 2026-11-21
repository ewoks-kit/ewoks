import pytest
from ewokscore.tests.examples.tasks.sumtask import SumTask

from ..task_utils import TaskExecutor


@pytest.mark.parametrize(
    "task", [SumTask, "ewokscore.tests.examples.tasks.sumtask.SumTask"]
)
def test_task_executor_class(task):
    assert TaskExecutor(task)(a=1, b=2) == {"result": 3}


@pytest.mark.parametrize("task", [max, "builtins.max"])
def test_task_executor_method(task):
    assert TaskExecutor(task)(1, 5, 3) == 5
