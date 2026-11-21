Execute one task
================

Execute one :term:`task <Task>` without a :term:`workflow` file.

From Python, call the task like a function:

.. code-block:: python

    from ewoks.task_utils import TaskExecutor

    sumtask = TaskExecutor("ewokscore.tests.examples.tasks.sumtask.SumTask")
    result = sumtask(a=10, b=20)  # {"result": 30}

    maximum = TaskExecutor("builtins.max")
    result = maximum(1, 5, 3)  # 5

From the command line, use ``--task``:

.. code-block:: bash

    ewoks execute ewokscore.tests.examples.tasks.sumtask.SumTask --task -pa a=10 -pa b=20
    ewoks execute builtins.max --task -pa 0=1 -pa 1=5 -pa 2=3

The task type is guessed from the task identifier. Use ``task_type`` to set it.

To execute a task in a :term:`worker`, use ``TaskSubmitter`` from
`ewoksjob <https://ewoksjob.readthedocs.io/>`_.
