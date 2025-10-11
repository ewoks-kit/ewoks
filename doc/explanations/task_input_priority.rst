Priority of task inputs
=======================

Details
-------

A node in a workflow can get inputs from three different sources:

1. Via the ``data_mapping`` link attribute of an incoming link (see `Link attributes <https://ewokscore.readthedocs.io/en/stable/definitions.html#link-attributes>`_)
2. Via the ``parameters`` CLI argument (or ``inputs`` for Python) when executing/submitting the workflow (see `ewoks execute reference <https://ewoks.readthedocs.io/en/stable/cli.html#ewoks-execute>`_)
3. Via the ``default_inputs`` node attribute of the node itself (see `Node attributes <https://ewokscore.readthedocs.io/en/stable/definitions.html#node-attributes>`_)

If the same input is specified by these different sources, *ewoks* applies the following priorities:

- **Data mapping takes precedence over workflow parameters and default inputs**
- If the input is not specified by the data mapping, **the workflow parameters takes precedence over the default inputs**
- If the input is not specified by the data mapping nor the workflow parameters, **default inputs are used as last resort**

TL;DR
-----

.. code-block::

    Data mapping > Workflow parameters > Node default inputs

Example
-------

Consider the following workflow made of `SumTask` nodes from `ewokscore` (`SumTask` takes two inputs `a` and `b` and sums them):

.. code-block:: python

    wf = {
        "graph": {"id": "Sum"},
        "nodes": [
            {
                "id": "sum_node",
                "task_type": "class",
                "task_identifier": "ewokscore.tests.examples.tasks.sumtask.SumTask",
                "default_inputs": [{"name": "a", "value": 1}, {"name": "b", "value": 2}],
            },
        ],
        "links": [],
    }


In this case, we have given two ``default_inputs`` to our ``sum_node``: 

- ``a = 1``
- ``b = 2``

If we execute the workflow with no parameters/inputs:

.. code-block:: python-console

    >>> execute_graph(graph=wf)
    {'result': 3}

There is no incoming link with data mapping, no workflow inputs, the two default inputs are summed to get ``3``.

---

If we specify a value for ``b`` when executing the workflow:

.. code-block:: python-console

    >>> execute_graph(
    ...     graph=wf,
    ...     inputs=[
    ...         {
    ...             "name": "b",
    ...             "value": 20,
    ...             "id": "sum_node",
    ...         }
    ...     ],
    ... )
    {'result': 21}

``a`` is still ``1`` but the default value of ``b`` was replaced by the workflow input value (``20``), changing to result to ``21``.

---

If we change our workflow to include a ``SumTask`` before our ``sum_node`` with an incoming data mapping that sets ``b`` value to its result (in this case ``200``):

.. code-block:: python

    new_wf = {
        "graph": {"id": "Sum"},
        "nodes": [
            {
                "id": "first_node",
                "task_type": "class",
                "task_identifier": "ewokscore.tests.examples.tasks.sumtask.SumTask",
                "default_inputs": [{"name": "a", "value": 100}, {"name": "b", "value": 100}],
            },
            {
                "id": "sum_node",
                "task_type": "class",
                "task_identifier": "ewokscore.tests.examples.tasks.sumtask.SumTask",
                "default_inputs": [{"name": "a", "value": 1}, {"name": "b", "value": 2}],
            },
        ],
        "links": [
            {
                "source": "first_node",
                "target": "sum_node",
                "data_mapping": [{"source_output": "result", "target_input": "b"}],
            }
        ],
    }

Then, if we execute as before (with the workflow input):

.. code-block:: python-console

    >>> execute_graph(
    ...     graph=new_wf,
    ...     inputs=[
    ...         {
    ...             "name": "b",
    ...             "value": 20,
    ...             "id": "sum_node",
    ...         }
    ...     ],
    ... )
    {'result': 201}

We see that both the default input and the workflow input for ``b`` of ``sum_node`` are ignored, the data mapping taking precedence to change the result to ``201``.
