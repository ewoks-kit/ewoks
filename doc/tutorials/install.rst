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

Limitations and caveats
-----------------------

Recreating a workflow environment does not guarantee that the workflow can be executed.
The requirements stored in a workflow describe the Python environment, but a workflow can
also depend on system software, external resources, configuration, or files that are not
captured by the requirements.

The workflow cannot be installed
++++++++++++++++++++++++++++++++

Environment creation can fail when the Python packages listed in the requirements cannot
be installed in the target environment. For example:

* A Python package requires a system package, compiler, or other native build dependency
  that is not available on the target machine.
* A package contains compiled code that is not compatible with the target operating system,
  CPU architecture, or Python version.
* A required package is no longer available from the configured package indexes, or requires
  access to a private package repository.
* A package has dependencies that cannot be resolved together with the required package versions.
* The Python version required by a package is not available on the target machine.
* Installing a package requires network access, credentials, a license, or another resource
  that is not available.
* The workflow was created on an operating system or architecture that is different from the
  target system and one or more packages are platform-specific.
* A package depends on external system libraries or runtime components that are not provided
  by the Python package itself.

The stored requirements can therefore make the Python environment reproducible,
but they cannot guarantee that the environment can be recreated on every machine.

The workflow can be installed but cannot be executed
++++++++++++++++++++++++++++++++++++++++++++++++++++

A successfully recreated Python environment only guarantees that the Python dependencies
can be installed. Execution can still fail because a task depends on resources or configuration
outside that environment. For example:

* A task input points to a file that does not exist on the target machine.
* A task expects a directory, executable, configuration file, or other resource that
  is not available.
* A task relies on an environment variable that is not defined in the target environment.
* A task requires access to an external service, database, network resource, or hardware device
  that is unavailable.
* A task requires credentials, secrets, or configuration that are not stored in the workflow.
* A task assumes a particular working directory or filesystem layout.
* A task uses operating-system features or commands that are not available on the target system.
* A task relies on data that was available when the workflow was created but has not been
  transferred with the workflow.
* A task dynamically imports or installs Python packages that are not declared in the
  workflow requirements.
* A task depends on a specific version or configuration of external software that is not captured
  by the Python environment.
* A task produces or consumes temporary files whose locations or permissions differ on
  the target machine.
* The workflow relies on non-deterministic external state, such as the current date, remote data,
  or the state of an external service.

In these cases, `ewoks install` can successfully recreate the Python environment, while `ewoks execute`
can still fail. The requirements should therefore be considered a description of the Python environment,
rather than a complete description of everything required to execute a workflow.
