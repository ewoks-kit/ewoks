.. _install_troubleshooting:

Limitations and caveats
=======================

Recreating a workflow environment does not guarantee that the workflow can be executed.
The requirements stored in a workflow describe the Python environment, but a workflow can
also depend on system software, external resources, configuration, or files that are not
captured by the requirements.

The workflow cannot be installed
--------------------------------

Environment creation can fail when the Python packages listed in the requirements cannot
be installed in the target environment. For example:

.. raw:: html

    <details><summary>Show the causes</summary>

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

.. raw:: html

    </details>

The stored requirements can therefore make the Python environment reproducible,
but they cannot guarantee that the environment can be recreated on every machine.

The workflow can be installed but cannot be executed
----------------------------------------------------

A successfully recreated Python environment only guarantees that the Python dependencies
can be installed. Execution can still fail because a task depends on resources or configuration
outside that environment. For example:

.. raw:: html

    <details><summary>Show the causes</summary>

* A task depends on files, directories, executables, or data that exist on the
  original machine but were not transferred to the target.
* A task relies on environment variables, credentials, secrets, or a specific
  filesystem layout that are not stored in the workflow.
* A task requires access to an external service, database, hardware device, or
  non-deterministic state (such as the current date or remote data) that is
  unavailable or differs on the target.
* A task uses operating-system features, commands, or external software —
  including packages imported or installed at runtime — that are not captured
  by the Python environment.

.. raw:: html

    </details>

In these cases, `ewoks install` can successfully recreate the Python environment, while `ewoks execute`
can still fail. The requirements should therefore be considered a description of the Python environment,
rather than a complete description of everything required to execute a workflow.
