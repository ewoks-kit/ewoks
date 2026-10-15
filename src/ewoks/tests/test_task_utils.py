import pytest

from ewoks.task_utils import execute_task, task_inputs
from ewokscore.tests.examples.tasks.sumtask import SumTask


@pytest.mark.parametrize("selector", ["id", "label", "task_identifier"])
def test_task_inputs(selector):
    inputs = task_inputs(**{selector: "task"}, inputs={"a": 1, "b": "test"})
    assert inputs == [
        {selector: "task", "name": "a", "value": 1},
        {selector: "task", "name": "b", "value": "test"},
    ]


@pytest.mark.parametrize(
    "task", [SumTask, "ewokscore.tests.examples.tasks.sumtask.SumTask"]
)
def test_execute_task(task):
    result = execute_task(task, inputs={"a": 1, "b": 1})
    assert result == {"result": 2}
