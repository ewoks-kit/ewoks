Getting started
===============

Install the Ewoks core libraries suite using ``pip``:

.. code-block:: bash

   pip install ewoks

This will include all core tools and example workflows.

Run an Example Workflow
-----------------------

The ``ewoks`` package includes several demo workflows. To run the ``demo`` workflow from the command line:

.. code-block:: bash

   ewoks execute demo -p a=10 -p b=3 --test --outputs=all

- ``-p a=10 -p b=3``: Set input parameters
- ``--test``: Load the ``demo`` workflow from Ewoks test suite
- ``--outputs=all``: Print outputs of all workflow nodes

For full CLI options, run:

.. code-block:: bash

   ewoks execute -h

Or refer to the `Command-line reference <../reference/cli.html>`_.

Inspect Workflow Parameters
----------------------------

Before executing a workflow, you can inspect its parameters using:

.. code-block:: bash

   ewoks show demo -p a=10 -p b=3 --test

Example output:

.. code-block:: text

   Workflow: demo
   Id: demo
   Description: demo
   ╒════════╤════════════════╤═══════════════════╤═══════╕
   │ Name   │ Value          │ Task identifier   │ Id    │
   ╞════════╪════════════════╪═══════════════════╪═══════╡
   │ list   │ [0, 1, 2]      │ SumList           │ task0 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ delay  │ 0              │ SumList           │ task0 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ b      │ <MISSING_DATA> │ SumTask           │ task1 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ delay  │ 0              │ SumTask           │ task1 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ a      │ 10             │ SumTask           │ task2 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ b      │ 3              │ SumTask           │ task2 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ delay  │ 0              │ SumTask           │ task2 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ b      │ 3              │ SumTask           │ task3 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ delay  │ 0              │ SumTask           │ task3 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ b      │ 4              │ SumTask           │ task4 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ delay  │ 0              │ SumTask           │ task4 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ delay  │ 0              │ SumTask           │ task5 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ b      │ 6              │ SumTask           │ task6 │
   ├────────┼────────────────┼───────────────────┼───────┤
   │ delay  │ 0              │ SumTask           │ task6 │
   ╘════════╧════════════════╧═══════════════════╧═══════╛

Convert Workflow Format
-----------------------

To inspect or modify a workflow, convert it to a JSON file:

.. code-block:: bash

   ewoks convert demo demo.json --test

Learn More
==========

.. note::

   **To go further**

   - **Create workflows in Python**

     See the `Hello World example <./hello_world.html>`_

   - **Use graphical interfaces**

     Explore the `GUI creation tools <../howtoguides/gui.html>`_

   - **Need specific guidance?**

     Check the `How-to guides <../howtoguides.html>`_

   - **Learn Ewoks step-by-step**

     The `Ewoks tutorial for developers <https://ewoksfordevs.readthedocs.io>`_ introduces all core concepts: workflows, tasks, and Ewoks tools.

     ℹ️ *This tutorial is regularly updated and used in ESRF training sessions.*