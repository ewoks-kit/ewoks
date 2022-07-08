Python
======

Install requirements

.. code:: bash

    python3 -m pip install ewoks

Execute a workflow

.. code:: python

    from ewoks import execute_graph

    result = execute_graph("/path/to/graph.json", binding=None)

The :doc:`hello world <../tutorials/hello_world>` example provides a small but complete example of
task implementation, workflow definition and workflow execution.

The *binding* argument can be

 * *ppf*: required to execute cyclic workflows
 * *dask*: required to parallelize workflow execution (thread, processes, cluster)
 * *orange*: required to execute workflows with a graphical interface

When no *binding* is specified it will use sequential execution in the current process.

Bindings can be installed as follows

.. code:: bash

    python3 -m pip install ewoks[orange,dask,ppf]

For more information see the `ewokscore documentation <https://ewokscore.readthedocs.io/>`_.
