Create workflows
================

This page demonstrates how to create an :term:`Ewoks` :term:`workflow` in Python.

.. note::

   For other ways of creating :term:`workflows <Workflow>`, see :doc:`./external`.

We want to create an :term:`Ewoks` :term:`workflow` that does the azimuthal integration of a detector image using `pyFAI <https://pyfai.readthedocs.io/en/stable/>`_ and saves the result as `HDF5/NeXus <https://www.nexusformat.org/>`_.

The :term:`workflow` will be composed of three :term:`tasks <Task>`:

- ``PyFaiConfig`` that will define the detector geometry
- ``IntegrateSinglePattern`` for the azimuthal integration
- ``SaveNexusPattern1D`` for the saving as HDF5/NeXus

These :term:`tasks <Task>` are part of the ``ewoksxrpd`` package.

.. note::

   The `Ewoks Task Catalog <https://ewoks.esrf.fr/en/latest/tasks/index.html>`_ lists :term:`Ewoks` :term:`tasks <Task>` provided by Python packages published on `PyPI <https://pypi.org/>`_.

   The :term:`tasks <Task>` used in this tutorial are described on the `SAXS/WAXS page <https://ewoks.esrf.fr/en/latest/tasks/saxs_waxs.html>`_ of the catalog.


Requirements
============

For this, we will firstly need to install the ``ewoks`` package

.. code-block:: bash

   pip install ewoks

but also the ``ewoksxrpd`` package that contains the :term:`tasks <Task>` we will use to create the :term:`workflow`.

.. code-block:: bash

   pip install ewoksxrpd

The image we will integrate can be downloaded from `the silx page <http://www.silx.org/pub/pyFAI/cookbook/calibration/Eiger4M_Al2O3_13.45keV.edf>`_ (*16MB*).

Finally, pyFAI needs a `PONI file <https://pyfai.readthedocs.io/en/stable/>`_ that describes the detector geometry. This file can be downloaded from `the silx page <http://www.silx.org/pub/pyFAI/cookbook/calibration/alpha-Al2O3.poni>`_ (*361B*).


Walkthrough
===========

An :term:`Ewoks` :term:`workflow` is represented in Python by a Python ``dict`` with three entries:

- ``nodes``: the list of the :term:`Ewoks` :term:`nodes` composing the :term:`workflow`. Each :term:`node <Nodes>` represent a :term:`task <Task>` that should be executed by the :term:`workflow`.
- ``links``: the list of :term:`links` between the :term:`nodes`. A :term:`link <Links>` between :term:`node <Nodes>` A and :term:`node <Nodes>` B is made to pass the outputs of :term:`node <Nodes>` A to the inputs of :term:`node <Nodes>` B.
- ``graph``: metadata of the :term:`workflow`.

Defining the nodes
------------------

:term:`Ewoks` :term:`nodes` are represented as Python ``dict``. Each entry of the dictionnary defines a characteristic of the :term:`node <Nodes>`. Lets illustrate this with the first :term:`node <Nodes>` that will define the detector geometry:

.. code-block:: python

   node1 = {
      "id": "config", 
      "task_identifier": "ewoksxrpd.tasks.pyfaiconfig.PyFaiConfig", 
      "task_type": "class"
   }

The Python ``dict`` contain three fields:

The first field ``id`` is mandatory: it serves as a unique identifier of the node in the :term:`workflow`. It will be used to define :term:`links` later.

The second field ``task_identifier`` defines which :term:`task <Task>` is used when this :term:`node <Nodes>` is executed. The identifier can be found in the `Task catalog <https://ewoks.esrf.fr/en/latest/tasks/saxs_waxs.html>`_.

The third field ``task_type`` defines the type of the :term:`task <Task>` defined by the ``task_identifier``. Almost all :term:`tasks <Task>` found in the `Task catalog <https://ewoks.esrf.fr/en/latest/tasks/index.html>`_ are ``class`` :term:`task <Task>` types.

----

The second :term:`node <Nodes>` will be responsible for azimuthal integration using ``IntegrateSinglePattern``:

.. code-block:: python

   node2 = {
      "id": "config", 
      "task_identifier": "ewoksxrpd.tasks.integrate.IntegrateSinglePattern", 
      "task_type": "class"
   }

We set the same fields as before with a different ``id``, since it is another :term:`node <Nodes>`, and a different ``task_identifier``, since the :term:`node <Nodes>` uses the ``IntegrateSinglePattern`` :term:`task <Task>` this time.

In a similar fashion, we define the last :term:`node <Nodes>` that will save the data using ``SaveNexusPattern1D``:

.. code-block:: python

   node3 = {
      "id": "save", 
      "task_identifier": "ewoksxrpd.tasks.nexus.SaveNexusPattern1D", 
      "task_type": "class"
   }

We end up then with the following :term:`workflow`:

.. image:: /_static/Workflow_no_link.svg
   :alt: Three workflow nodes: one called config, one called integrate and the last called save

We now need to create :term:`links` to define the :term:`node <Nodes>` execution order and to pass data from one :term:`node <Nodes>` to the next.

Defining the links
------------------

Similarly to :term:`nodes`, :term:`links` are represented as Python ``dict`` with entries defining their characteristics. In our workflow, we need two :term:`links`:

- one that connects the configuration :term:`node <Nodes>` ``config`` (the source) to the integration :term:`node <Nodes>` ``integrate`` (the target)
- one that connects the integration :term:`node <Nodes>` ``integrate`` (the source) to the saving :term:`node <Nodes>` ``save`` (the target)

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

The ``source`` and ``target`` fields are used to define the source and target :term:`nodes` via the ``id`` defined in the previous section about :term:`nodes`.

Since the :term:`task <Task>` of the source :term:`node <Nodes>` has several outputs and the :term:`task <Task>` of the target :term:`node <Nodes>` has several inputs, we need to specify which output correspond to which input: this is the role of the ``data_mapping`` field.

In a sense, an :term:`Ewoks` :term:`link <Links>` is composed of several "one-to-one" :term:`links` that link one output to one input. The ``data_mapping`` field is a list in which each entry defines a "one-to-one" :term:`link <Links>` between a ``source_output``, identified by its output name, and a ``target_input``, identified by its input name. Input and output names are part of the :term:`Ewoks` :term:`task <Task>` definition and can be found there.

In this case, we link the output named ``detector`` of the ``PyfaiConfig`` :term:`task <Task>` to the input name ``detector`` of the ``IntegrateSinglePattern`` :term:`task <Task>` (and same for ``geometry`` and ``energy``). It just so happens that both have the same name.

----

Secondly, we need to pass the data produced by the ``integrate`` :term:`node <Nodes>` to the ``save`` :term:`node <Nodes>` that will save the data. For this, we will create a second :term:`link <Links>`:

.. code-block:: python

   link2 = {
      "source": "integrate", 
      "target": "save", 
      "data_mapping": [
         {"source_output": "radial", "target_input": "x"}, 
         {"source_output": "intensity", "target_input": "y"}
      ]
   }

This time, we link the output named ``radial`` of the ``IntegrateSinglePattern`` :term:`task <Task>` to the input named ``x`` of the ``SaveNexusPattern1D`` :term:`task <Task>`, demonstrating how :term:`links` can connect outputs and inputs of different names. Similarly, we link the output named ``intensity`` of the integration :term:`task <Task>` to the input named ``y`` of the saving :term:`task <Task>`.

Define the workflow
-------------------

Now that the :term:`nodes` and :term:`link <Links>` are defined, all is left is to build a Python ``dict`` representing the :term:`workflow`

.. code-block:: python

   workflow = {
      "nodes": [node1, node2, node3], 
      "links": [link1, link2], 
      "graph": {"id": "integrate_save"}
   }

Visually, the :term:`workflow` now looks like this:

.. image:: /_static/Workflow_with_links.svg
   :alt: Three workflow nodes: one called config, one called integrate and the last called save. There is a link between the config and integrate nodes and another one between the integrate and save nodes.


To go further
=============

We demonstrated here how to create a simple :term:`workflow` from Python objects. For more complex :term:`workflows <Workflow>`, you may want to use `EwoksWeb <https://ewoksweb.readthedocs.io>`_ instead, a web-based GUI to design :term:`workflows <Workflow>`. In :term:`Ewoksweb`, you can drag and drop :term:`nodes` in a canvas, link them together and :term:`Ewoksweb` will create the :term:`workflow` file for you.

Also, so far, we did not run the :term:`workflow`. :term:`workflow` execution is the focus of another tutorial that can be found in the :doc:`./execute` page.

Finally, this tutorial only covers the required fields of the :term:`nodes`, :term:`links` and :term:`workflow` dictionaries to build a working :term:`Ewoks` :term:`workflow`. The `Ewoks specification page <https://ewokscore.readthedocs.io/en/stable/reference/specs.html>`_ documents all the possible fields and their explanation.


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
