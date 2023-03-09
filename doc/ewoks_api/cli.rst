Command line
============

Install requirements

.. code:: bash

    python3 -m pip install ewoks

Execute a workflow

.. code:: bash

    ewoks execute /path/to/graph.json [--engine dask]

or for an installation with the system python

.. code:: bash

    python3 -m ewoks execute /path/to/graph.json [--engine dask]

The *ewoks* command line interface can be used for other things like converting a workflow format

.. code:: bash

    ewoks execute /path/to/graph.ows /path/to/graph.json

*Ewoks* jobs can be submitted as follows

.. code:: bash

    ewoks submit /path/to/graph.json

For more information

.. code:: bash

    ewoks --help