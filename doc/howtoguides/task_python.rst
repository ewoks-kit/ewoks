Execute a task from Python
==========================

Walkthrough
-----------

This page shows to instantiate a task from Python, set its inputs, execute it and retrieve its outputs. It can be useful for debugging a single task for example.

To illustrate it, we will use the `SumTask` below that adds two numbers `a` and `b`, and stores the result in `result`:

.. code:: python

    class SumTask(
        Task, input_names=["a"], optional_input_names=["b"], output_names=["result"]
    ):
        def run(self):
            result = self.inputs.a
            if self.inputs.b:
                result += self.inputs.b
            self.outputs.result = result


.. admonition:: Tip

    This task can be imported from ``ewokscore.tests.examples.tasks.sumtask``

Task inputs need to be set via the ``inputs`` argument when creating the task before executing via ``execute``:

.. code:: python

    >>> task = SumTask(inputs={"a": 5, "b": 10})
    >>> task.execute()

The results can then be retrieved from ``outputs`` or using ``get_output_value``:

.. code:: python

    >>> task.outputs["result"]
    15
    >>> task.get_output_value('result')
    15

Limitations
-----------

Inputs cannot be modified once the task is instantiated

.. code:: python

     >>> task = SumTask(inputs={"a": 5, "b": 10})
     >>> task.inputs.a = 10
     ...
     ewokscore.variable.ReadOnlyVariableError: a

A new task instance needs to be created to execute it with different inputs

.. code:: python

     >>> task = SumTask(inputs={"a": 10, "b": 10})
     >>> task.execute()
     >>> task.get_output_value("result")
     20

Outputs will be missing before the task is executed. More specifically, the outputs are set to `MISSING_DATA <https://ewokscore.readthedocs.io/en/latest/_generated/ewokscore.task.Task.html#ewokscore.task.Task.MISSING_DATA>`_ until they are set by the execution: 

.. code:: python

    >>> task = SumTask(inputs={"a": 5, "b": 10})
    >>> task.get_output_value("result")
    <MISSING_DATA>

Full code
---------

.. code:: python

    from ewokscore.tests.examples.tasks.sumtask import SumTask

    task = SumTask(inputs={"a": 5, "b": 10})
    task.execute()
    print(task.get_output_value("result"))
