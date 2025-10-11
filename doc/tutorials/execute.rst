Execute workflows
=================

Ewoks workflows can be executed via several interfaces and with several workflow engines.

The :ref:`python interface <execute_python>` for executing workflows is a function

.. code-block:: python

    from ewoks import execute_graph

    result = execute_graph("/path/to/graph.json", engine=None)

The equivalent exists for the :ref:`command-line <cli>`.

The :code:`engine=None` argument selects the default engine. Documentation on different engines:

* `ewoksppf <https://ewoksppf.readthedocs.io/>`_ : execute cyclic workflows
* `ewoksdask <https://ewoksdask.readthedocs.io/>`_ : parallel and distributed workflow execution
* `ewoksorange <https://ewoksorange.readthedocs.io/>`_ : execute with desktop GUI

Documentation on other interfaces than python and the command-line interface:

* `ewoksweb <https://ewoksweb.readthedocs.io/>`_ : execute with web GUI
* `ewoksserver <https://ewoksweb.readthedocs.io/>`_ : execute with REST API
* `ewoksjob <https://ewoksweb.readthedocs.io/>`_ : job scheduling for Ewoks workflows
