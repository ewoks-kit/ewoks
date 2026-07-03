Choosing an engine for execution
=================================

Ewoks workflows can be executed using several engines, each with its own capabilities:

- `Dask <https://www.dask.org/>`_: Distributed and parallel computing framework.
- `Pypushflow <https://pypushflow.readthedocs.io/>`_: Scheduler for acyclic and cyclic task graphs.
- `Orange <https://orangedatamining.com/>`_: Visual programming and data visualization platform.

New engines can be added following the :doc:`./new_engine` procedure.

Using a Supported Engine
------------------------

To run workflows with a specific engine, install the appropriate extra:

.. code-block:: bash

   pip install ewoks[dask]     # For Dask
   pip install ewoks[ppf]      # For Pypushflow
   pip install ewoks[orange]   # For Orange

If no engine is installed, Ewoks defaults to a basic sequential engine (``"core"``).

To specify the engine explicitly, use the ``--engine`` option:

.. code-block:: bash

   ewoks execute --test demo --engine dask

.. warning::

   **Orange execution is GUI-driven** and cannot run without the Orange GUI.

   Running:

   .. code-block:: bash

      ewoks execute --test demo --engine orange

   ...will open the Orange GUI, where you can edit the workflow.

   To execute it:

   - Double-click on ``task0`` in the workflow.
   - Use the **Trigger** button in the **Task** widget.

   For guidance, see `Orange's getting started docs <https://orangedatamining.com/getting-started/>`_.


Engine Feature Comparison
-------------------------

Some engines support more advanced features, like loops or GUI interaction:

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

   **Native support** means that Ewoks tasks can be executed without modification.

   For Orange, you must wrap each Ewoks task in a corresponding Orange widget. See the
   `Orange widget tutorial <https://ewoksorange.readthedocs.io/en/stable/tutorials/my_first_widget.html>`_
   in the ``ewoksorange`` documentation.

