Choosing an engine for execution
=================================

:term:`Ewoks` :term:`workflows <Workflow>` can be executed using several :term:`execution engines <Execution engine>`, each with its own capabilities:

- `Dask <https://www.dask.org/>`_: Distributed and parallel computing framework.
- `Pypushflow <https://pypushflow.readthedocs.io/>`_: Scheduler for acyclic and cyclic :term:`task <Task>` graphs.
- `Orange <https://orangedatamining.com/>`_: Visual programming and data visualization platform.

New :term:`execution engines <Execution engine>` can be added following the :doc:`./new_engine` procedure.

Using a Supported Engine
------------------------

To run :term:`workflows <Workflow>` with a specific :term:`execution engine <Execution engine>`, install the appropriate extra:

.. code-block:: bash

   pip install ewoks[dask]     # For Dask
   pip install ewoks[ppf]      # For Pypushflow
   pip install ewoks[orange]   # For Orange

If no :term:`execution engine <Execution engine>` is installed, :term:`Ewoks` defaults to a basic sequential :term:`execution engine <Execution engine>` (``"core"``).

To specify the :term:`execution engine <Execution engine>` explicitly, use the ``--engine`` option:

.. code-block:: bash

   ewoks execute --test demo --engine dask

.. warning::

   **Orange execution is GUI-driven** and cannot run without the Orange GUI.

   Running:

   .. code-block:: bash

      ewoks execute --test demo --engine orange

   ...will open the Orange GUI, where you can edit the :term:`workflow`.

   To execute it:

   - Double-click on ``task0`` in the :term:`workflow`.
   - Use the **Trigger** button in the **Task** widget.

   For guidance, see `Orange's getting started docs <https://orangedatamining.com/getting-started/>`_.


Engine Feature Comparison
-------------------------

Some :term:`execution engines <Execution engine>` support more advanced features, like loops or GUI interaction:

.. raw:: html
 
   <table class="table">
   <thead>
   <tr>
     <th>engine</th>
     <th>Loops</th>
     <th>Conditional Links</th>
     <th>Parallel execution</th>
     <th>Interaction (GUI)</th>
     <th>Native support</th>
   </tr>
   </thead>
   <tbody>
   <tr>
     <td><code>core</code></td>
     <td class="red">✗</td>
     <td class="red">✗</td>
     <td class="red">✗</td>
     <td class="red">✗</td>
     <td class="green">✓</td>
   </tr>
   <tr>
     <td><code>dask</code></td>
     <td class="red">✗</td>
     <td class="red">✗</td>
     <td class="green">✓</td>
     <td class="red">✗</td>
     <td class="green">✓</td>
   </tr>
   <tr>
     <td><code>ppf</code></td>
     <td class="green">✓</td>
     <td class="green">✓</td>
     <td class="green">✓</td>
     <td class="red">✗</td>
     <td class="green">✓</td>
   </tr>
   <tr>
     <td><code>"orange"</code></td>
     <td class="red">✗</td>
     <td class="red">✗</td>
     <td class="orange">✓</td>
     <td class="green">✓</td>
     <td class="red">✗</td>
   </tr>
   </tbody>
   </table>



.. note::

   **Native support** means that :term:`Ewoks` :term:`tasks <Task>` can be executed without modification.

   For Orange, you must wrap each :term:`Ewoks` :term:`task <Task>` in a corresponding Orange widget. See the
   `Orange widget tutorial <https://ewoksorange.readthedocs.io/en/stable/tutorials/my_first_widget.html>`_
   in the ``ewoksorange`` documentation.
