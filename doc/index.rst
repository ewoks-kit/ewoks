ewoks |release|
===============

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.6075054.svg
   :target: https://doi.org/10.5281/zenodo.6075054

Many `workflow management systems <https://s.apache.org/existing-workflow-systems>`_ exist to deal with data processing
problems that can be expressed as a graph of tasks, also referred to as a *computational graph* or *workflow*. The main
purpose of a workflow management system is to provide a framework for implementing tasks, creating graphs of tasks and
executing these graphs.

The purpose of *ewoks* is to provide an abstraction layer between graph representation and execution. This allows using
the same tasks and graphs in different workflow management systems. *ewoks* itself is **not** a workflow management system.

*ewoks* has been developed by the `Software group <http://www.esrf.eu/Instrumentation/software>`_ of the `European Synchrotron <https://www.esrf.eu/>`_.

Getting started
---------------

Install *ewoks*

.. code:: bash

    python -m pip install ewoks

Execute a workflow from the command line

.. code:: bash

    ewoks execute /path/to/graph.json

Ewoks has different interfaces to execute an ewoks workflow

.. toctree::
    :maxdepth: 1

    ewoks_api/python
    ewoks_api/cli
    ewoks_api/job
    ewoks_api/rest
    ewoks_api/qt
    ewoks_api/web

Documentation
-------------

.. toctree::
    :maxdepth: 1

    tutorials/hello_world
    tutorials/ewoks_events
    tutorials/running_workflows
    api

Binding documentation:
----------------------

 * `ewokscore <https://ewokscore.readthedocs.io/>`_ : create workflows and implement tasks
 * `ewoksorange <https://ewoksorange.readthedocs.io/>`_ : create and execute workflows with a desktop GUI
 * `ewoksppf <https://ewoksppf.readthedocs.io/>`_ : execute cyclic workflows
 * `ewoksdask <https://ewoksdask.readthedocs.io/>`_ : parallelize workflow execution
 * `ewoksjob <https://ewoksjob.readthedocs.io/>`_: distribute workflow execution
 * `ewoksserver <https://ewoksjob.readthedocs.io/>`_: REST server to manage and execute workflows
 * `ewoksweb <https://ewoksjob.readthedocs.io/>`_: web frontend to create, visualize and execute workflows