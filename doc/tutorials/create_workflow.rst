Ewoks workflow creation tutorial
================================

This page demonstrates how to create an Ewoks workflow from Python.

.. note::

   For other ways of creating workflows, see :doc:`./external`.

We want to create an Ewoks workflow that does the azimuthal integration of a detector image using `pyFAI <https://pyfai.readthedocs.io/en/stable/>`_ and saves the result as `HDF5/NeXus <https://www.nexusformat.org/>`_.

The workflow will be composed of three tasks:

- ``PyFaiConfig`` that will define the detector geometry
- ``IntegrateSinglePattern`` for the azimuthal integration
- ``SaveNexusPattern1D`` for the saving as HDF5/NeXus

These tasks are part of the ``ewoksxrpd`` package.

.. note::

   See the `Task catalog page <https://ewoks.esrf.fr/en/latest/tasks/index.html>`_ to see the existing Ewoks tasks and which package needs to be installed to use them.

   For example, the tasks we will use can be found on the `SAXS/WAXS page <https://ewoks.esrf.fr/en/latest/tasks/saxs_waxs.html>`_


Requirements
============

For this, we will firstly need to install the ``ewoks`` package

.. code-block:: bash

   pip install ewoks

but also the ``ewoksxrpd`` package that contains the tasks we will use to create our workflows.

.. code-block:: bash

   pip install ewoksxrpd

The image we will integrate can be downloaded from `the silx page <http://www.silx.org/pub/pyFAI/cookbook/calibration/Eiger4M_Al2O3_13.45keV.edf>`_ (*16MB*).

Finally, pyFAI needs a `PONI file <https://pyfai.readthedocs.io/en/stable/>`_ that describes the detector geometry. This file can be downloaded from `the silx page <http://www.silx.org/pub/pyFAI/cookbook/calibration/alpha-Al2O3.poni>`_ (*361B*).


Walkthrough
===========

An Ewoks workflow is represented in Python by a Python ``dict`` with three entries:

- ``nodes``: the list of the Ewoks nodes composing the workflow. Each node represent a task that should be executed by the workflow.
- ``links``: the list of links between the nodes. A link between node A and node B is made to pass the outputs of node A to the inputs of node B.
- ``graph``: metadata of the workflow.

Defining the nodes
------------------

Ewoks nodes are represented as Python ``dict``. Each entry of the dictionnary defines a characteristic of the node. Let"s illustrate this with our first node that will define the detector geometry:

.. code-block:: python

   node1 = {
      "id": "config", 
      "task_identifier": "ewoksxrpd.tasks.pyfaiconfig.PyFaiConfig", 
      "task_type": "class"
   }

The Python ``dict`` contain three fields:

The first field ``id`` is mandatory: it serves as unique identifier of the node in the workflow. It will notably used to define links later.

The second field ``task_identifier`` tells which task should used when this node is executed. The identifier can be found in the `Task catalog page <https://ewoks.esrf.fr/en/latest/tasks/saxs_waxs.html>`_.

The third field ``task_type`` defines the type of the task defined by the ``task_identifier``. Almost all tasks found in the `Task catalog <https://ewoks.esrf.fr/en/latest/tasks/index.html>`_ are ``class`` task types.

----

The second node will be responsible for azimuthal integration using ``IntegrateSinglePattern``:

.. code-block:: python

   node2 = {
      "id": "config", 
      "task_identifier": "ewoksxrpd.tasks.integrate.IntegrateSinglePattern", 
      "task_type": "class"
   }

We set the same fields as before but changing ``id``, since it is another node, and ``task_identifier``, since the node uses the ``IntegrateSinglePattern`` task this time.

In a similar fashion, we define the last node that will save the data using ``SaveNexusPattern1D``:

.. code-block:: python

   node3 = {
      "id": "save", 
      "task_identifier": "ewoksxrpd.tasks.nexus.SaveNexusPattern1D", 
      "task_type": "class"
   }

We end up then with the following workflow:

.. image:: /_static/Workflow_no_link.svg
   :alt: Three workflow nodes: one called config, one called integrate and the last called save

We now need to define the links to structure our workflow and pass data from one node to the next.

Defining the links
------------------

Similarly to nodes, links are represented as Python ``dict`` with entries defining their characteristics. In our workflow, we need two links:

- one that connects the configuration node ``config`` (the source) to the integration node ``integrate`` (the target)
- one that connects the integration node ``integrate`` (the source) to the saving node ``save`` (the target)

.. code-block:: python

   link1 = {
      "source": "config", 
      "target": "integrate", 
      "data_mapping": [
         {"source_output": "detector", "target_input": "detector"}, 
         {"source_output": "geometry", "target_input": "geometry"}, 
         {"source_output": "energy", "target_input": "energy"}
      ]
   }

The ``source`` and ``target`` fields are used to define the source and target nodes via the ``id`` defined in the previous section about nodes.

Since the task of the source node has several outputs and the task of the target node has several inputs, we need to specify which output correspond to which input: this is the role of the ``data_mapping`` field.

In a sense, an Ewoks link is composed of several "one-to-one" links that link one output to one input. The ``data_mapping`` field is a list in which each entry defines a "one-to-one" link between a ``source_output``, identified by its output name, and a ``target_input``, identified by its input name. Input and output names are part of the Ewoks task definition and can be found there.

In this case, we link the output named ``detector`` of the ``PyfaiConfig`` task to the input name ``detector`` of the ``IntegrateSinglePattern`` task (and same for ``geometry`` and ``energy``). It just so happens that both have the same name.

----

Secondly, we need to pass the data produced by the ``integrate`` node to the ``save`` node that will save the data. For this, we will create a second link:

.. code-block:: python

   link2 = {
      "source": "integrate", 
      "target": "save", 
      "data_mapping": [
         {"source_output": "radial", "target_input": "x"}, 
         {"source_output": "intensity", "target_input": "y"}
      ]
   }

This time, we link the output named ``radial`` of the ``IntegrateSinglePattern`` task to the input named ``x`` of the ``SaveNexusPattern1D`` task, demonstrating how links can connect outputs and inputs of different names. Similarly, we link the output named ``intensity`` of the integration task to the input named ``y`` of the saving task.

Putting the workflow together
-----------------------------

Now that the nodes and link are defined, all is left is to build our Python ``dict`` representing the workflow

.. code-block:: python

   workflow = {
      "nodes": [node1, node2, node3], 
      "links": [link1, link2], 
      "graph": {"id": "integrate_save"}
   }

Visually, the workflow now looks like this:

.. image:: /_static/Workflow_with_links.svg
   :alt: Three workflow nodes: one called config, one called integrate and the last called save. There is a link between the config and integrate nodes and another one between the integrate and save nodes


To go further
=============

We demonstrate here how to create a simple workflow from Python objects. For more complex workflows, you may use `EwoksWeb <https://ewoksweb.readthedocs.io>`_ instead, a web-based GUI to design workflows. In *EwoksWeb*, you can drag and drop nodes in a canvas, link them together and EwoksWeb will create the workflow file for you.

Also, so far, we did not run the workflow. Workflow execution is the focus of another tutorial that can be found in the `How to execute a workflow <./execute_workflow.html>`_ page.

Finally, this tutorial only covers the required fields of the nodes, links and workflow dictionaries to build a working Ewoks workflow. The `Ewoks specification page <https://ewokscore.readthedocs.io/en/stable/reference/specs.html>`_ gathers all the possible fields and their explanation.


Full code
=========

.. code-block:: python

   node1 = {
       "id": "integrate",
       "task_identifier": "ewoksxrpd.tasks.integrate.Integrate1D",
       "task_type": "class",
   }
   node2 = {
       "id": "save",
       "task_identifier": "ewoksxrpd.tasks.nexus.SaveNexusPattern1D",
       "task_type": "class",
   }
   node3 = {
       "id": "save",
       "task_identifier": "ewoksxrpd.tasks.nexus.SaveNexusPattern1D",
       "task_type": "class",
   }


   link1 = {
       "source": "config",
       "target": "integrate",
       "data_mapping": [
           {"source_output": "detector", "target_input": "detector"},
           {"source_output": "geometry", "target_input": "geometry"},
           {"source_output": "energy", "target_input": "energy"},
       ],
   }
   link2 = {
       "source": "integrate",
       "target": "save",
       "data_mapping": [
           {"source_output": "radial", "target_input": "x"},
           {"source_output": "intensity", "target_input": "y"},
       ],
   }

   workflow = {
       "nodes": [node1, node2, node3],
       "links": [link1, link2],
       "graph": {"id": "integrate_save"},
   }