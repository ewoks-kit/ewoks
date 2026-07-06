Adding a new :term:`execution engine <Execution engine>` to :term:`Ewoks`
=========================================================================

This page shows how to create a custom :term:`execution engine <Execution engine>` named ``"abc"`` which can be used like this

.. code-block:: bash

   ewoks execute --test demo --engine abc

Create a Python package with the appropriate entry point in ``pyproject.toml``:

.. code-block:: toml

   [project]
   name = "ewoksabc"

   [project.entry-points."ewoks.engines"]
   "abc" = "ewoksabc.engine:AbcWorkflowEngine"

Your :term:`execution engine <Execution engine>` must implement the abstract interface ``WorkflowEngine`` from ``ewokscore``:

.. code-block:: python

   from ewokscore.graph import TaskGraph
   from ewokscore.engine_interface import WorkflowEngine

   class AbcWorkflowEngine(WorkflowEngine):

       def execute_graph(self, graph: TaskGraph, ...) -> Optional[dict]:
           ...


(Optional) :term:`Workflow` Serialization Support
-------------------------------------------------

If your :term:`execution engine <Execution engine>` also handles :term:`workflow` (de)serialization (e.g., from ``.xyz`` files), add another entry point:

.. code-block:: toml

   [project.entry-points."ewoks.engines.serialization.representations"]
   "xyz" = "ewoksabc.engine:AbcWorkflowEngine"

Your :term:`execution engine <Execution engine>` should implement ``WorkflowEngineWithSerialization``:

.. code-block:: python

   from ewokscore.engine_interface import WorkflowEngineWithSerialization

   class AbcWorkflowEngine(WorkflowEngineWithSerialization):

       def execute_graph(self, graph: TaskGraph, ...) -> Optional[dict]:
           ...

       def deserialize_graph(self, graph: Any, ...) -> TaskGraph:
           ...

       def serialize_graph(self, graph: TaskGraph, ...) -> Any:
           ...

       def get_graph_representation(self, graph: Any) -> Optional[str]:
           ...

This allows :term:`Ewoks` to recognize and delegate serialization/deserialization to your :term:`execution engine <Execution engine>` when the `ewoksabc` package is installed.
