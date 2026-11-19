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

Both sides use a :term:`package manager`. The walk-throughs below do the same thing with each
of the supported ones

.. toctree::
    :maxdepth: 1

    install/pip_venv
    install/uv
    install/poetry
    install/conda
    install/pixi
    install/bootstrap
    install/troubleshooting

The producer and the re-producer do not need the same :term:`package manager`: the
requirements contain the installed python packages, which any :term:`package manager` can
install. See :ref:`this how-to guide <requirements>` to select a :term:`package manager`.

Store the requirements
----------------------

``ewoks convert`` saves the packages installed in the current python environment as the
``requirements`` of the destination :term:`workflow`. The ``requirements`` field of the
``graph`` field looks like this

.. literalinclude:: ../_snippets/requirements.json
    :language: json

* ``bootstrap`` are the versions of :term:`ewoks` and of the engine that saved the
  :term:`workflow`: ``ewokscore`` for a ``.json`` or ``.yaml`` file and ``ewoksorange`` for an
  ``.ows`` file.
* ``distributions`` are the installed python packages. Any :term:`package manager` can
  recreate the environment from this list.
* ``manager`` is the :term:`package manager` that generated the requirements. Its ``files``
  are what the package manager needs to recreate the environment exactly. pip-venv and
  conda store what the environment reports (``pip freeze``, ``conda env export``). uv,
  poetry and pixi store the project files of the environment, for example a
  ``pyproject.toml`` and a lock file, and store nothing when there are none. Without
  ``files``, ``distributions`` describe the environment.

Create the environment
----------------------

``ewoks install`` creates a python environment for the :term:`workflow`. It prints the python
interpreter of the environment it created, the command to execute the :term:`workflow` in it
and the command to remove it again. These commands work from any terminal and directory

.. code-block:: text

    Installed requirements for demo.json
      Python : /home/user/ewoks_envs/demo/bin/python
      Execute: /home/user/ewoks_envs/demo/bin/python -m ewoks execute /home/user/demo.json
      Remove : rm -rf /home/user/ewoks_envs/demo

Without ``--yes`` you are asked to confirm after the packages have been listed. The
walk-throughs use ``--env-root`` to create the environment in the working directory. Without
it the environment is created where the :term:`package manager` creates named environments.

``ewoks install`` needs a python environment with :term:`ewoks`. See
:ref:`this page <install_bootstrap>` to create the environment of a :term:`workflow` with
nothing but a :term:`package manager`.

Execute the workflow
--------------------

``--env`` executes the :term:`workflow` with the python interpreter of that environment
instead of the current one. This works because the requirements contain ``ewoks`` itself: it
was installed in the environment in which the :term:`workflow` was converted. When they do
not, add ``--with-ewoks`` to ``ewoks install`` to install it. The versions coming from the
:term:`workflow` are kept, unless they come from project files that allow other versions: a
warning lists the versions that changed.

Remove the environment
----------------------

The environment is a normal directory, so removing it is enough. This is the command that
``ewoks install`` prints when it creates the environment.

Limitations and caveats
-----------------------

Recreating the environment does not guarantee that the :term:`workflow` can be installed or
executed. See :ref:`this page <install_troubleshooting>`.
