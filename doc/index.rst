ewoks |version|
===============

.. image:: https://img.shields.io/badge/DOI-10.1080/08940886.2024.2432305-blue
   :target: https://doi.org/10.1080/08940886.2024.2432305

Many `workflow management systems <https://s.apache.org/existing-workflow-systems>`_ exist to
deal with data processing problems that can be expressed as a graph of tasks, also referred
to as a *computational graph* or *workflow*. The main purpose of a workflow management system
is to provide a framework for implementing tasks, creating graphs of tasks and executing these graphs.

The purpose of *ewoks* (Extensible Workflow System) is to provide an abstraction layer between graph
representation and execution. This allows using the same tasks and graphs in different workflow management systems.

*ewoks* has been developed by the `Software group <http://www.esrf.eu/Instrumentation/software>`_
of the `European Synchrotron <https://www.esrf.eu/>`_.

.. admonition:: Quick Start

   Install ewoks

   .. code-block:: bash

      pip install ewoks

   Execute the demo workflow

   .. code-block:: bash

      ewoks execute demo --test

.. toctree::
    :hidden:
    
    tutorials/index
    howtoguides/index
    explanations/index
    reference/index
