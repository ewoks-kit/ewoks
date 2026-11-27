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

Both sides use a :term:`package manager`. They do not need the same one: the requirements
contain the installed python packages, which any :term:`package manager` can install. See
:ref:`the how-to guide on reproducing a workflow environment <requirements>` to select a
:term:`package manager`.

The producer converts the :term:`workflow`. The re-producer installs the environment and
executes the :term:`workflow` in it. See the :ref:`CLI reference <cli>` for all arguments

.. code-block:: bash

    ewoks convert demo demo.json --test
    ewoks install demo.json --yes
    ewoks execute --env ~/.ewoks/envs/demo demo.json --outputs=all

Producer side
-------------

``ewoks convert`` saves the packages installed in the current python environment as the
``requirements`` of the destination :term:`workflow`. The :term:`workflow` stores them in
``graph.requirements``. They look like this

.. literalinclude:: ../_snippets/requirements.json
    :language: json

* ``bootstrap`` are the versions of :term:`ewoks` and of the engine that saved the
  :term:`workflow`: ``ewokscore`` for a ``.json`` or ``.yaml`` file and ``ewoksorange`` for an
  ``.ows`` file.
* ``python`` is the python interpreter: its version, implementation, compiler and build.
* ``system`` is the operating system and the hardware: its name, release, version, machine
  and processor.
* ``distributions`` are the installed python packages. Any :term:`package manager` can
  recreate the environment from this list.
* ``manager`` is the :term:`package manager` that generated the requirements. Its ``files``
  are what the package manager needs to recreate the environment exactly. pip-venv and
  conda store what the environment reports (``pip freeze``, ``conda env export``). uv,
  poetry and pixi store the project files of the environment, for example a
  ``pyproject.toml`` and a lock file, and store nothing when there are none. Without
  ``files``, the ``distributions`` list describes the environment.

Use ``ewoks convert --exclude-requirements`` to store nothing.

Re-producer side
----------------

The re-producer side has three steps: install the environment with ``ewoks install`` or
:ref:`without ewoks <install_bootstrap>`, execute the :term:`workflow` in it and, when it is
not needed anymore, remove it.

Install with ewoks
++++++++++++++++++
``ewoks install`` creates a python environment for the :term:`workflow`. For example

.. code-block:: bash

    ewoks install demo.json --yes --env-root /tmp/ewoks_envs

It prints the python interpreter of the environment it created, the command to execute the
:term:`workflow` in it and the command to remove it again. These commands work from any
terminal and directory

.. code-block:: text

    Installed requirements for demo.json
      Python : /tmp/ewoks_envs/demo/bin/python
      Execute: /tmp/ewoks_envs/demo/bin/python -m ewoks execute /home/user/demo.json
      Remove : rm -rf /tmp/ewoks_envs/demo

Without ``--yes``, ``ewoks install`` asks you to confirm after it has listed the packages.
``--env-root`` creates the environment in the given directory. Without it, ``ewoks install`` creates the environment where the
:term:`package manager` creates named environments.

``ewoks execute --env`` needs :term:`ewoks` in the environment. The requirements contain it
when the :term:`workflow` was converted in an environment with :term:`ewoks`. When they do
not, add ``--with-ewoks`` to ``ewoks install`` to install it. The versions coming from the
:term:`workflow` are kept, unless they come from project files that allow other versions: a
warning lists the versions that changed.

Install without ewoks
+++++++++++++++++++++

``ewoks install`` needs a python environment with :term:`ewoks`. See
:ref:`Install without ewoks <install_bootstrap>` to create the environment of a
:term:`workflow` on a machine that has a :term:`package manager` but no :term:`ewoks`.

Execute the workflow
++++++++++++++++++++

``ewoks execute --env`` executes the :term:`workflow` with the python interpreter of the
environment that ``ewoks install`` created, instead of the current one

.. code-block:: bash

    ewoks execute --env /tmp/ewoks_envs/demo demo.json --outputs=all

Remove the environment
++++++++++++++++++++++

The environment is a normal directory, so removing it is enough. This is the command that
``ewoks install`` prints when it creates the environment.

Limitations and caveats
-----------------------

Recreating the environment does not guarantee that the :term:`workflow` can be installed or
executed. See :ref:`Limitations and caveats <install_troubleshooting>`.

.. toctree::
    :maxdepth: 1
    :caption: Walk-through per package manager

    install/pip_venv
    install/uv
    install/poetry
    install/conda
    install/pixi

.. toctree::
    :maxdepth: 1
    :caption: More

    install/bootstrap
    install/troubleshooting
