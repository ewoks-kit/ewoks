.. _install_tutorial:

Install and execute a workflow
==============================

A :term:`workflow` needs the python packages of its :term:`tasks <Task>` to be installed.
:term:`Ewoks` can store the python environment in which a :term:`workflow` was created inside
the :term:`workflow` itself and recreate that environment later, on another machine or at
another time.

There are two sides to this

* the *producer* creates a :term:`workflow` and stores its requirements,
* the *re-producer* receives the :term:`workflow`, recreates the environment and executes the
  :term:`workflow` in it.

Both sides use a :term:`package manager`. The walk-through below does both sides

.. toctree::
    :maxdepth: 1

    install/pip_venv

The producer and the re-producer do not need the same :term:`package manager`: the
requirements contain the installed python packages, which any :term:`package manager` can
install. See :ref:`this how-to guide <requirements>` to select a :term:`package manager`.

Store the requirements
----------------------

``ewoks convert`` saves the packages installed in the current python environment as the
``requirements`` of the destination :term:`workflow`. The ``requirements`` field of the
``graph`` field looks like this

.. code-block:: json

    {
        "python": {"version": "3.12.11", "implementation": "CPython", "...": "..."},
        "system": {"system": "Linux", "machine": "x86_64", "...": "..."},
        "distributions": [
            {"name": "ewokscore", "version": "5.1.0", "installer": "pip"},
            {"name": "networkx", "version": "3.4.2", "installer": "pip"}
        ],
        "manager": {
            "name": "pip-venv",
            "version": "25.0.1",
            "files": {"requirements.txt": "ewokscore==5.1.0\nnetworkx==3.4.2\n"}
        }
    }

* ``distributions`` are the installed python packages. Any :term:`package manager` can
  recreate the environment from this list.
* ``manager`` is the :term:`package manager` that generated the requirements together with
  the files it needs to recreate the environment exactly, for example a lock file.

Create the environment
----------------------

``ewoks install`` creates a python environment for the :term:`workflow`. It prints the python
interpreter of the environment it created, the command to execute the :term:`workflow` in it
and the command to remove it again

.. code-block:: text

    Installed requirements for demo.json
      Python : ewoks_envs/demo/bin/python
      Execute: ewoks execute --env ewoks_envs/demo demo.json
      Remove : rm -rf ewoks_envs/demo

Without ``--yes`` you are asked to confirm after the packages have been listed. The
walk-through uses ``--env-root`` to create the environment in the working directory. Without
it the environment is created where the :term:`package manager` creates named environments.

Execute the workflow
--------------------

``--env`` executes the :term:`workflow` with the python interpreter of that environment
instead of the current one. This works because the requirements contain ``ewoks`` itself: it
was installed in the environment in which the :term:`workflow` was converted. When they do
not, add ``--with-ewoks`` to ``ewoks install`` to install it without changing any of the
versions coming from the :term:`workflow`.

Remove the environment
----------------------

The environment is a normal directory, so removing it is enough. This is the command that
``ewoks install`` prints when it creates the environment.
