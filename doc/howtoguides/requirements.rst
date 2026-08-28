.. _requirements:

Reproduce a workflow environment
================================

A :term:`workflow` stores the python environment it was created in as the ``requirements``
field of its ``graph`` field. ``ewoks install`` recreates that environment and
``ewoks execute --env`` runs the :term:`workflow` in it. See
:ref:`this tutorial <install_tutorial>` for a step-by-step example.

What is stored
--------------

``ewoks convert`` and ``ewoks execute -o convert_destination=...`` store

* ``python`` and ``system``: the python interpreter and the operating system.
* ``distributions``: every installed python package with its version and, when it was not
  installed from the python package index, the git commit or the archive it came from. Any
  :term:`package manager` can recreate the environment from this list.
* ``manager``: the :term:`package manager` that generated the requirements, with the content
  of the files it needs to recreate the environment: ``requirements.txt`` for pip-venv,
  ``pyproject.toml`` and ``uv.lock`` for uv.

Use ``--exclude-requirements`` to store nothing.

.. note::

    A :term:`workflow` that stores a list of requirements instead of the structure above is
    still supported: the list is parsed as a ``requirements.txt`` file.

Select a package manager
------------------------

``ewoks convert`` uses the :term:`package manager` of the current python environment. It is
detected from the environment variables and files that package managers leave behind, and
from the tool that installed most of the packages. Use ``--package-manager-name`` to select
one explicitly

.. code-block:: bash

    ewoks convert demo demo.json --test --package-manager-name uv

``ewoks install`` uses the :term:`package manager` that generated the requirements, unless it
is not installed on the machine. It installs the stored files of that :term:`package manager`.
When the requirements do not contain them, or installing them fails, it generates its own
files from the ``distributions`` list and installs those instead. Both installations are
confirmed separately unless ``--yes`` is provided

.. code-block:: bash

    ewoks install demo.json --yes --package-manager-name uv

``--package-manager-command`` provides the command that invokes the tool, for example when it
is not on the ``PATH`` or when a faster implementation should be used

.. code-block:: bash

    ewoks install demo.json --yes --package-manager-name uv \
        --package-manager-command /path/to/uv

Choose the environment
----------------------

.. code-block:: bash

    # a root directory of your choice instead of the one of the package manager
    ewoks install demo.json --yes --env-root /tmp/envs

    # a name of your choice instead of the workflow identifier
    ewoks install demo.json --yes --env-name demo-env

    # remove the environment when it already exists
    ewoks install demo.json --yes --clean

    # another python version than the one stored in the requirements
    ewoks install demo.json --yes --python-version 3.12

    # add ewoks itself when the requirements do not contain it
    ewoks install demo.json --yes --with-ewoks

    # install in the current python environment instead of creating one
    ewoks install demo.json --yes --in-place

The default name is the identifier of the :term:`workflow`, which is the ``id`` field of its
``graph`` field. A :term:`workflow` without an identifier gets a name derived from its
content.

Without ``--env-root`` the :term:`package manager` decides where the environment goes. venv
and uv create an environment wherever they are told to, so for pip-venv and uv ewoks uses
``~/.ewoks/envs``.

An environment that already exists is installed in, which adds the requirements to what is
already there. Use ``--clean`` to remove it first. Only a directory that contains a python
environment is removed.

The environment of a :term:`workflow` is a directory: for pip-venv it is a virtual
environment and for uv a project with the environment in ``.venv``. ``ewoks execute --env``
takes that directory, not the python interpreter inside it.

Limitations
-----------

* ``--python-version`` is a request: uv can provide any python version but pip-venv can only
  use the version of the python interpreter that creates the environment. A warning is emitted
  when the version cannot be provided.
* uv resolves the ``distributions`` into a lock file, which requires access to the package
  index. When that fails, a warning is emitted and the requirements are stored without files:
  the environment is then recreated from the ``distributions`` list.
* A lock file is only read by a :term:`package manager` that understands its format version, so
  reproducing an environment can require a version of the tool that is at least as recent as
  the one that generated the requirements.
* A package installed from a local directory cannot be recreated elsewhere. This is reported as
  a warning when the requirements are generated.
