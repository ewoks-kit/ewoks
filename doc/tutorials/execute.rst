Execute workflows
=================

:term:`Ewoks` :term:`workflows <Workflow>` can be executed via several interfaces and with several :term:`execution engines <Execution engine>`.

The :ref:`python interface <execute_python>` for executing :term:`workflows <Workflow>` is a function

.. code-block:: python

    from ewoks import execute_graph

    result = execute_graph("/path/to/graph.json", engine=None)

The equivalent exists for the :ref:`command-line <cli>`.

The :code:`engine=None` argument selects the default :term:`execution engine <Execution engine>`. Documentation on different :term:`execution engines <Execution engine>`:

* `ewoksppf <https://ewoksppf.readthedocs.io/>`_ : execute cyclic :term:`workflows <Workflow>`
* `ewoksdask <https://ewoksdask.readthedocs.io/>`_ : parallel and distributed :term:`workflow` execution
* `ewoksorange <https://ewoksorange.readthedocs.io/>`_ : execute with desktop GUI

Documentation on other interfaces than python and the command-line interface:

* `ewoksweb <https://ewoksweb.readthedocs.io/>`_ : execute with web GUI
* `ewoksserver <https://ewoksweb.readthedocs.io/>`_ : execute with REST API
* `ewoksjob <https://ewoksweb.readthedocs.io/>`_ : job scheduling for :term:`Ewoks` :term:`workflows <Workflow>`
