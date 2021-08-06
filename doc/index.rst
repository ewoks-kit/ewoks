ewoks |release|
===============

ewoks is a container project that allow installing the core library and optionally bindings for Workflow Management Systems.

ewoks has been developed by the `Software group <http://www.esrf.eu/Instrumentation/software>`_ of the `European Synchrotron <https://www.esrf.eu/>`_.

The core library is used to represent graphs and the bindings are used to execute them:

.. code:: bash

    from ewokscore import load_graph
    from ewoksppf import execute_graph

    result = execute_graph(load_graph("/path/to/graph.json"))

Tutorials
---------

.. toctree::
    :maxdepth: 1

    tutorials/running_workflows

Binding documentation:
----------------------

 * `ewokscore <https://workflow.gitlab-pages.esrf.fr/ewoks/ewokscore>`_ : create workflows and implement tasks
 * `ewoksorange <https://workflow.gitlab-pages.esrf.fr/ewoks/ewoksorange>`_ : create and execute workflows with a GUI
 * `ewoksppf <https://workflow.gitlab-pages.esrf.fr/ewoks/ewoksppf>`_ : execute cyclic workflows
 * `ewoksdask <https://workflow.gitlab-pages.esrf.fr/ewoks/ewoksdask>`_ : distributed workflow execution
