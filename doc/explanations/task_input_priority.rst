Priority of :term:`task <Task>` inputs
======================================

Details
-------

A :term:`node <Nodes>` in a :term:`workflow` can get inputs from three different sources:

1. Via the ``data_mapping`` :term:`link <Links>` attribute of an incoming :term:`link <Links>` (see `Link attributes <https://ewokscore.readthedocs.io/en/stable/definitions.html#link-attributes>`_)
2. Via the ``parameters`` CLI argument (or ``inputs`` for Python) when executing/submitting the :term:`workflow` (see `ewoks execute reference <https://ewoks.readthedocs.io/en/stable/cli.html#ewoks-execute>`_)
3. Via the ``default_inputs`` :term:`node <Nodes>` attribute of the :term:`node <Nodes>` itself (see `Node attributes <https://ewokscore.readthedocs.io/en/stable/definitions.html#node-attributes>`_)

If the same input is specified by these different sources, :term:`Ewoks` applies the following priorities:

- Data mapping takes precedence over :term:`workflow` parameters and default inputs.
- If the input is not specified by the data mapping, the :term:`workflow` parameters takes precedence over the default inputs.
- If the input is not specified by the data mapping nor the :term:`workflow` parameters, default inputs are used as last resort.

TL;DR
-----

.. code-block::

    Data mapping > Workflow parameters > Node default inputs

Example
-------

Consider the following :term:`workflow` made of `SumTask` :term:`nodes` from `ewokscore` (`SumTask` takes two inputs `a` and `b` and sums them):

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

There is no incoming :term:`link <Links>` with data mapping, no :term:`workflow` inputs, the two default inputs are summed to get ``3``.

---

If we specify a value for ``b`` when executing the :term:`workflow`:

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

``a`` is still ``1`` but the default value of ``b`` was replaced by the :term:`workflow` input value (``20``), changing to result to ``21``.

---

If we change our :term:`workflow` to include a ``SumTask`` before our ``sum_node`` with an incoming data mapping that sets ``b`` value to its result (in this case ``200``):

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

Then, if we execute as before (with the :term:`workflow` input):

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

We see that both the default input and the :term:`workflow` input for ``b`` of ``sum_node`` are ignored, the data mapping taking precedence to change the result to ``201``.
