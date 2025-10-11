Getting started
===============

Install *ewoks*

.. code-block:: bash

	pip install ewoks

Create a test workflow in JSON format (“acyclic1” is an test workflow that ships with ewoks)

.. code-block:: bash

	ewoks convert acyclic1 --test test.json

Inspect workflow parameters before executing the workflow

.. code-block:: bash

   Inspect the demo workflow

.. code-block:: bash

	ewoks show test.json

Execute a workflow and print the output of all tasks

.. code-block:: bash

	ewoks execute test.json --outputs all

For a desktop GUI, install *ewoks* with the orange binding

.. code-block:: bash

	pip install ewoks[orange]

Open the test workflow in the GUI

.. code-block:: bash

	ewoks execute test.json --engine orange

For a web GUI, install *ewoksserver* with the frontend

.. code-block:: bash

	pip install ewoksserver[frontend]

Start the *ewoks* web server, open the link in a web browser and load the `test.json` file

.. code-block:: bash

	ewoks-server
