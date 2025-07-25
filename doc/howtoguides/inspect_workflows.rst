Inspect Workflow Inputs
=======================

Ewoks workflows use input parameters that can be configured for each node.
This tutorial demonstrates how to inspect and verify these input parameters using several methods.

We'll use the `demo` workflow from the Ewoks test suite as an example.
Convert it to JSON format with the following command:

.. code:: bash

    ewoks convert demo example.json --test

Command-Line Inspection
-----------------------

To view the input parameters defined in a workflow, use the `ewoks show` command:

.. code:: bash

    ewoks show example.json

This displays all input parameters, their values, and the workflow node they belong to:

.. code:: bash

    Workflow: example.json
    Id: demo
    Description: demo
    ╒════════╤════════════════╤═══════════════════╤═══════╕
    │ Name   │ Value          │ Task identifier   │ Id    │
    ╞════════╪════════════════╪═══════════════════╪═══════╡
    │ list   │ [0, 1, 2]      │ SumList           │ task0 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumList           │ task0 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumTask           │ task1 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ <MISSING_DATA> │ SumTask           │ task1 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ a      │ 2              │ SumTask           │ task2 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumTask           │ task2 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ <MISSING_DATA> │ SumTask           │ task2 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumTask           │ task3 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ 3              │ SumTask           │ task3 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumTask           │ task4 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ 4              │ SumTask           │ task4 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumTask           │ task5 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumTask           │ task6 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ 6              │ SumTask           │ task6 │
    ╘════════╧════════════════╧═══════════════════╧═══════╛

Parameters with `<MISSING_DATA>` do not have a value. If a missing parameter is **required**, it is marked with a `(*)`. For example:

.. code:: bash

    Workflow: example.json
    Id: demo
    Description: demo
    ╒════════╤════════════════╤═══════════════════╤═══════╕
    │ Name   │ Value          │ Task identifier   │ Id    │
    ╞════════╪════════════════╪═══════════════════╪═══════╡
    │ a⁽*⁾   │ <MISSING_DATA> │ SumTask           │ task2 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ list   │ [0, 1, 2]      │ SumList           │ task0 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumList           │ task0 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ <MISSING_DATA> │ SumTask           │ task1 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumTask           │ task1 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ <MISSING_DATA> │ SumTask           │ task2 │
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
    ⁽*⁾ Value is required for execution.

In this case, the `a` parameter for task `SumTask` at node `task2` is required and must be provided before execution.

Workflow nodes can be identified by:

- **Task identifier** – the identifier of the code to be executed.
- **Id** – the unique identifier of the node within the workflow.
- **Label** (if present) – a human-readable tag, which may not be unique.

If no labels are defined, the `Label` column is omitted from the output.

Validating Execution Arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To override workflow parameters for execution, use the `-p` option:

.. code:: bash

    ewoks execute example.json -p SumTask:delay=99 --input-node-id taskid

Before executing the workflow, you can verify that your arguments are applied as intended using `ewoks show` with the same arguments:

.. code:: bash

    ewoks show example.json -p SumTask:delay=99 --input-node-id taskid

The output will reflect the overridden `delay` values:

.. code:: bash

    Workflow: example.json
    Id: demo
    Description: demo
    ╒════════╤════════════════╤═══════════════════╤═══════╕
    │ Name   │ Value          │ Task identifier   │ Id    │
    ╞════════╪════════════════╪═══════════════════╪═══════╡
    │ list   │ [0, 1, 2]      │ SumList           │ task0 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 0              │ SumList           │ task0 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 99             │ SumTask           │ task1 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ <MISSING_DATA> │ SumTask           │ task1 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ a      │ 2              │ SumTask           │ task2 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 99             │ SumTask           │ task2 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ <MISSING_DATA> │ SumTask           │ task2 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 99             │ SumTask           │ task3 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ 3              │ SumTask           │ task3 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 99             │ SumTask           │ task4 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ 4              │ SumTask           │ task4 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 99             │ SumTask           │ task5 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ delay  │ 99             │ SumTask           │ task6 │
    ├────────┼────────────────┼───────────────────┼───────┤
    │ b      │ 6              │ SumTask           │ task6 │
    ╘════════╧════════════════╧═══════════════════╧═══════╛

The value before the colon in `-p <target>:<parameter>=<value>` refers to the node identifier, which defaults to the `Id` column.
You can change this behavior with the `--input-node-id` option to use the `Label` or `Task identifier` instead.

Graphical Interfaces
--------------------

You can also inspect input parameters using graphical tools.

Desktop GUI
~~~~~~~~~~~

To use the :ref:`desktop GUI <ewoks-canvas>` based on Orange:

.. code:: bash

    ewoks execute example.json --engine=orange -p SumTask:delay=99 --input-node-id taskid

Then double-click on each node to inspect or edit parameters:

.. image:: images/inspect_desktop.png
    :alt: Double-click on each node to inspect input parameters.

Web GUI
~~~~~~~

To inspect parameters via the :ref:`web interface <ewoksweb>`:

1. Convert the workflow while applying overrides:

    .. code:: bash

        ewoks convert example.json example_with_params.json --test -p SumTask:delay=99 --input-node-id taskid

2. Start the web server:

    .. code:: bash

        ewoksweb

    You should see:

    .. code:: bash

        INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

3. Open the workflow file in your browser:

    .. image:: images/inspect_web_open.png
        :alt: Open the workflow file from disk in the web UI.

4. Click on a node to view or edit its parameters:

    .. image:: images/inspect_web_node.png
        :alt: Click on each node to inspect input parameters.
