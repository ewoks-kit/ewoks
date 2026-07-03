Adding a new engine to Ewoks
============================

This page shows how to create a custom engine named ``"abc"`` which can be used like this

.. code-block:: bash

   ewoks execute --test demo --engine abc

Create a Python package with the appropriate entry point in ``pyproject.toml``:

.. code-block:: toml

   [project]
   name = "ewoksabc"

   [project.entry-points."ewoks.engines"]
   "abc" = "ewoksabc.engine:AbcWorkflowEngine"

Your engine must implement the abstract interface ``WorkflowEngine`` from ``ewokscore``:

.. code-block:: python

   from ewokscore.graph import TaskGraph
   from ewokscore.engine_interface import WorkflowEngine

   class AbcWorkflowEngine(WorkflowEngine):

       def execute_graph(self, graph: TaskGraph, ...) -> Optional[dict]:
           ...


(Optional) Workflow Serialization Support
------------------------------------------

If your engine also handles workflow (de)serialization (e.g., from ``.xyz`` files), add another entry point:

.. code-block:: toml

   [project.entry-points."ewoks.engines.serialization.representations"]
   "xyz" = "ewoksabc.engine:AbcWorkflowEngine"

Your engine should implement ``WorkflowEngineWithSerialization``:

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

This allows Ewoks to recognize and delegate serialization/deserialization to your engine when the `ewoksabc` package is installed.