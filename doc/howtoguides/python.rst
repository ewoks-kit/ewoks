.. _execute_python:

Execute a :term:`workflow` from Python
======================================

Install requirements

.. code-block:: bash

    pip install ewoks

Execute a :term:`workflow`

.. code-block:: python

    from ewoks import execute_graph

    result = execute_graph("/path/to/graph.json", engine=None)

The :ref:`hello world <hello_world>` example provides a small but complete example of
:term:`task <Task>` implementation, :term:`workflow` definition and :term:`workflow` execution.

The *engine* argument can be

 * *ppf*: required to execute cyclic :term:`workflows <Workflow>`
 * *dask*: required to parallelize :term:`workflow` execution (thread, processes, cluster)
 * *orange*: required to execute :term:`workflows <Workflow>` with a graphical interface

When no *engine* is specified it will use sequential execution in the current process.

Bindings can be installed as follows

.. code-block:: bash

    pip install ewoks[orange,dask,ppf]

For more information see the `ewokscore documentation <https://ewokscore.readthedocs.io/>`_.
