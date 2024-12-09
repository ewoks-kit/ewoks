ewoks |version|
===============

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.6075053.svg
   :target: https://doi.org/10.5281/zenodo.6075053

Many `workflow management systems <https://s.apache.org/existing-workflow-systems>`_ exist to deal with data processing
problems that can be expressed as a graph of tasks, also referred to as a *computational graph* or *workflow*. The main
purpose of a workflow management system is to provide a framework for implementing tasks, creating graphs of tasks and
executing these graphs.

The purpose of *ewoks* (Extensible Workflow System) is to provide an abstraction layer between graph representation and execution.
This allows using the same tasks and graphs in different workflow management systems.

*ewoks* has been developed by the `Software group <http://www.esrf.eu/Instrumentation/software>`_ of the `European Synchrotron <https://www.esrf.eu/>`_.

Getting started
---------------

Install *ewoks*

.. code:: bash

	pip install ewoks

Create a test workflow in JSON format (“acyclic1” is an test workflow that ships with ewoks)

.. code:: bash

	ewoks convert acyclic1 --test test.json

Execute the test workflow and print the output of all tasks

.. code:: bash

	ewoks execute test.json --outputs all

For a desktop GUI, install *ewoks* with the orange binding

.. code:: bash

	pip install ewoks[orange]

Open the test workflow in the GUI

.. code:: bash

	ewoks execute test.json --engine orange

For a web GUI, install *ewoksserver* with the frontend

.. code:: bash

	pip install ewoksserver[frontend]

Start the *ewoks* web server, open the link in a web browser and load the `test.json` file

.. code:: bash

	ewoks-server


.. toctree::
    :hidden:
    
    hello_world
    cli
    howtoguides
    explanations
    api



Further Ewoks documentation
---------------------------

About creating and editing workflows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* `ewoks tutorial on workflow creation <https://ewoks.esrf.fr/en/latest/tutorials/create_workflow.html>`_: create a workflow from the Python interface
* `ewoksorange <https://ewoksorange.readthedocs.io/>`_ : create and execute workflows with a desktop GUI
* `ewoksweb <https://ewoksweb.readthedocs.io/>`_: web frontend to create, visualize and execute workflows
* `ewokscore <https://ewokscore.readthedocs.io/>`_ : create workflows and implement tasks

About executing workflows
^^^^^^^^^^^^^^^^^^^^^^^^^

* `ewoksppf <https://ewoksppf.readthedocs.io/>`_ : execute cyclic workflows
* `ewoksdask <https://ewoksdask.readthedocs.io/>`_ : parallelize workflow execution

About setting up infrastructure for workflow execution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* `ewoksjob <https://ewoksjob.readthedocs.io/>`_: distribute workflow execution
* `ewoksserver <https://ewoksserver.readthedocs.io/>`_: REST server to manage and execute workflows

About developping Ewoks
^^^^^^^^^^^^^^^^^^^^^^^

* `ewoksutils <https://ewoksutils.readthedocs.io/>`_ : developer utilities

