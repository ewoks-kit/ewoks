ewoks |release|
===============

Many `workflow management systems <https://s.apache.org/existing-workflow-systems>`_ exist to deal with data processing problems that can be expressed as a graph of tasks, also referred to as a *computational graph* or *workflow*. The main purpose of a workflow management system is to provide a framework for implementing tasks, creating graphs of tasks and executing these graphs.

The purpose of *ewoks* is to provide an abstraction layer between graph representation and execution. This allows using the same tasks and graphs in different workflow management systems. *ewoks* itself is **not** a workflow management system.

*ewoks* has been developed by the `Software group <http://www.esrf.eu/Instrumentation/software>`_ of the `European Synchrotron <https://www.esrf.eu/>`_.

Workflows can be loaded and executed from the command line

.. code:: bash

    ewoks execute /path/to/graph.json [--binding dask]

or from python

.. code:: python

    from ewoks import execute_graph

    result = execute_graph("/path/to/graph.json", binding="dask")

When no binding is specified it will use sequential execution from `ewokscore`.

Getting started
---------------

When installing without any options, only `ewokscore` will be installed

.. code:: bash

    python -m pip install ewoks[orange,dask,ppf,test]

The core project `ewokscore` and the optional bindings can be tested after installation like this

.. code:: bash

    pytest --pyargs ewokscore.tests
    pytest --pyargs ewoksorange.tests
    pytest --pyargs ewoksppf.tests
    pytest --pyargs ewoksdask.tests

A simple :doc:`hello world <tutorials/hello_world>` introduces task implementation, workflow definition and workflow execution.

Tutorials
---------

.. toctree::
    :maxdepth: 1

    tutorials/hello_world
    tutorials/running_workflows

Binding documentation:
----------------------

 * `ewokscore <https://workflow.gitlab-pages.esrf.fr/ewoks/ewokscore>`_ : create workflows and implement tasks
 * `ewoksorange <https://workflow.gitlab-pages.esrf.fr/ewoks/ewoksorange>`_ : create and execute workflows with a GUI
 * `ewoksppf <https://workflow.gitlab-pages.esrf.fr/ewoks/ewoksppf>`_ : execute cyclic workflows
 * `ewoksdask <https://workflow.gitlab-pages.esrf.fr/ewoks/ewoksdask>`_ : distributed workflow execution
