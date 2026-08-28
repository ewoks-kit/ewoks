.. _install_poetry:

poetry
======

End-to-end walk-through with `poetry <https://python-poetry.org/>`_ 1.8 or later. Poetry works
with projects instead of environments: its commands need a directory with a
``pyproject.toml`` file, selected with ``-C``.

Install poetry
--------------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            export POETRY_HOME=$HOME/.local/poetry
            curl -sSL https://install.python-poetry.org | python3 -
            export PATH=$POETRY_HOME/bin:$PATH

    .. group-tab:: macOS

        .. code-block:: bash

            export POETRY_HOME=$HOME/.local/poetry
            curl -sSL https://install.python-poetry.org | python3 -
            export PATH=$POETRY_HOME/bin:$PATH

    .. group-tab:: Windows

        .. code-block:: powershell

            $env:POETRY_HOME = "$env:USERPROFILE\.local\poetry"
            (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
            $env:PATH = "$env:POETRY_HOME\bin;$env:PATH"

Producer side
-------------

Create a project, install :term:`ewoks` in it and store a :term:`workflow` with the packages
of that project as its ``requirements``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            poetry new ewoks_producer
            poetry -C ewoks_producer add ewoks
            poetry -C ewoks_producer run ewoks convert demo "$PWD/demo.json" --test

    .. group-tab:: macOS

        .. code-block:: bash

            poetry new ewoks_producer
            poetry -C ewoks_producer add ewoks
            poetry -C ewoks_producer run ewoks convert demo "$PWD/demo.json" --test

    .. group-tab:: Windows

        .. code-block:: powershell

            poetry new ewoks_producer
            poetry -C ewoks_producer add ewoks
            poetry -C ewoks_producer run ewoks convert demo "$PWD\demo.json" --test

Install any package that provides :term:`tasks <Task>` instead of
``ewoks`` for a real :term:`workflow`. Poetry 2 resolves the arguments of ``poetry run``
relative to the project directory, so the workflow paths are absolute.

Re-producer side
----------------

Only ``ewoks`` itself is needed to recreate the environment of ``demo.json``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            poetry new ewoks_reproducer
            poetry -C ewoks_reproducer add ewoks
            poetry -C ewoks_reproducer run ewoks install "$PWD/demo.json" --yes --env-root "$PWD/ewoks_envs"

    .. group-tab:: macOS

        .. code-block:: bash

            poetry new ewoks_reproducer
            poetry -C ewoks_reproducer add ewoks
            poetry -C ewoks_reproducer run ewoks install "$PWD/demo.json" --yes --env-root "$PWD/ewoks_envs"

    .. group-tab:: Windows

        .. code-block:: powershell

            poetry new ewoks_reproducer
            poetry -C ewoks_reproducer add ewoks
            poetry -C ewoks_reproducer run ewoks install "$PWD\demo.json" --yes --env-root "$PWD\ewoks_envs"

The environment of the :term:`workflow` is a poetry project in ``ewoks_envs/demo`` with the
virtual environment in its ``.venv`` directory.

Execute the workflow
--------------------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            poetry -C ewoks_reproducer run ewoks execute --env "$PWD/ewoks_envs/demo" "$PWD/demo.json" --outputs=all

    .. group-tab:: macOS

        .. code-block:: bash

            poetry -C ewoks_reproducer run ewoks execute --env "$PWD/ewoks_envs/demo" "$PWD/demo.json" --outputs=all

    .. group-tab:: Windows

        .. code-block:: powershell

            poetry -C ewoks_reproducer run ewoks execute --env "$PWD\ewoks_envs\demo" "$PWD\demo.json" --outputs=all

Clean up
--------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            rm -rf ewoks_producer ewoks_reproducer ewoks_envs demo.json

    .. group-tab:: macOS

        .. code-block:: bash

            rm -rf ewoks_producer ewoks_reproducer ewoks_envs demo.json

    .. group-tab:: Windows

        .. code-block:: powershell

            Remove-Item -Recurse -Force ewoks_producer, ewoks_reproducer, ewoks_envs, demo.json
