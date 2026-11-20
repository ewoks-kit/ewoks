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

A :term:`workflow` with requirements comes from one of two sources.

Download the demo workflow
++++++++++++++++++++++++++

Download the demo :term:`workflow` of this documentation

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            curl -LsSfO |docs_url|/demo.json

    .. group-tab:: macOS

        .. code-block:: bash

            curl -LsSfO |docs_url|/demo.json

    .. group-tab:: Windows

        .. code-block:: powershell

            irm |docs_url|/demo.json -OutFile demo.json

Use your own workflow
+++++++++++++++++++++

Create a project, install :term:`ewoks` and ``mytasks`` in it and store your :term:`workflow`
with the packages of that project as its ``requirements``. The environment is created inside
the project, so that its ``pyproject.toml`` and ``poetry.lock`` are stored as well.

* ``mytasks``: the packages that provide the :term:`tasks <Task>` of your :term:`workflow`.
* ``myworkflow.json``: your :term:`workflow`. See :doc:`how to create a workflow <../create_workflow>`.

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            poetry new ewoks_producer
            poetry -C ewoks_producer config virtualenvs.in-project true --local
            poetry -C ewoks_producer add ewoks mytasks
            poetry -C ewoks_producer run ewoks convert "$PWD/myworkflow.json" "$PWD/myworkflow_requirements.json"

    .. group-tab:: macOS

        .. code-block:: bash

            poetry new ewoks_producer
            poetry -C ewoks_producer config virtualenvs.in-project true --local
            poetry -C ewoks_producer add ewoks mytasks
            poetry -C ewoks_producer run ewoks convert "$PWD/myworkflow.json" "$PWD/myworkflow_requirements.json"

    .. group-tab:: Windows

        .. code-block:: powershell

            poetry new ewoks_producer
            poetry -C ewoks_producer config virtualenvs.in-project true --local
            poetry -C ewoks_producer add ewoks mytasks
            poetry -C ewoks_producer run ewoks convert "$PWD\myworkflow.json" "$PWD\myworkflow_requirements.json"

Re-producer side
----------------

Only ``ewoks`` itself is needed to recreate the environment of ``demo.json``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            poetry new ewoks_reproducer
            poetry -C ewoks_reproducer config virtualenvs.in-project true --local
            poetry -C ewoks_reproducer add ewoks
            poetry -C ewoks_reproducer run ewoks install "$PWD/demo.json" --yes --env-root "$PWD/ewoks_envs"

    .. group-tab:: macOS

        .. code-block:: bash

            poetry new ewoks_reproducer
            poetry -C ewoks_reproducer config virtualenvs.in-project true --local
            poetry -C ewoks_reproducer add ewoks
            poetry -C ewoks_reproducer run ewoks install "$PWD/demo.json" --yes --env-root "$PWD/ewoks_envs"

    .. group-tab:: Windows

        .. code-block:: powershell

            poetry new ewoks_reproducer
            poetry -C ewoks_reproducer config virtualenvs.in-project true --local
            poetry -C ewoks_reproducer add ewoks
            poetry -C ewoks_reproducer run ewoks install "$PWD\demo.json" --yes --env-root "$PWD\ewoks_envs"

The environment of the :term:`workflow` is a poetry project in ``ewoks_envs/demo`` with the
virtual environment in its ``.venv`` directory.

Alternatively, the :ref:`ewoks-install script <install_bootstrap>` recreates the
environment without an environment with :term:`ewoks`

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            curl -LsSf |docs_url|/ewoks-install.sh | sh -s -- demo.json

    .. group-tab:: macOS

        .. code-block:: bash

            curl -LsSf |docs_url|/ewoks-install.sh | sh -s -- demo.json

    .. group-tab:: Windows

        .. code-block:: powershell

            & ([scriptblock]::Create((irm |docs_url|/ewoks-install.ps1))) demo.json

It selects the :term:`package manager` itself and prints the command to execute the
:term:`workflow` in the environment it creates.

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
