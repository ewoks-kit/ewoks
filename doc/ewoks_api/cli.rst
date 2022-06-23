Command line
============

Install requirements

.. code:: bash

    python -m pip install ewoks

Execute a workflow

.. code:: bash

    ewoks execute /path/to/graph.json [--binding dask]

The *ewoks* command line interface can be used for other things like converting a workflow format

.. code:: bash

    ewoks execute /path/to/graph.ows /path/to/graph.json -s indent=2

For more information

.. code:: bash

    ewoks --help