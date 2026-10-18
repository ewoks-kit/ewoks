.. _install_uv:

uv
==

End-to-end walk-through of `workflow installation and execution <../install.rst>`_
with `uv <https://docs.astral.sh/uv/>`_.

Install uv
----------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            export UV_INSTALL_DIR=$HOME/.local/uv/bin  # default location
            curl -LsSf https://astral.sh/uv/install.sh | INSTALLER_NO_MODIFY_PATH=1 sh
            export PATH=$UV_INSTALL_DIR:$PATH

    .. group-tab:: macOS

        .. code-block:: bash

            export UV_INSTALL_DIR=$HOME/.local/uv/bin  # default location
            curl -LsSf https://astral.sh/uv/install.sh | INSTALLER_NO_MODIFY_PATH=1 sh
            export PATH=$UV_INSTALL_DIR:$PATH

    .. group-tab:: Windows

        .. code-block:: powershell

            $env:UV_INSTALL_DIR = "$env:USERPROFILE\.local\uv\bin"  # default location
            irm https://astral.sh/uv/install.ps1 | iex
            $env:PATH = "$env:UV_INSTALL_DIR;$env:PATH"

Producer side
-------------

Create a uv project, add :term:`ewoks` to it and store a :term:`workflow` with the
packages of its environment as its ``requirements``. The ``pyproject.toml`` and ``uv.lock``
of the project are stored as well.

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            uv init ewoks_producer
            uv add --project ewoks_producer ewoks
            uv run --project ewoks_producer ewoks convert demo demo.json --test

    .. group-tab:: macOS

        .. code-block:: bash

            uv init ewoks_producer
            uv add --project ewoks_producer ewoks
            uv run --project ewoks_producer ewoks convert demo demo.json --test

    .. group-tab:: Windows

        .. code-block:: powershell

            uv init ewoks_producer
            uv add --project ewoks_producer ewoks
            uv run --project ewoks_producer ewoks convert demo demo.json --test

Install any package that provides :term:`tasks <Task>` instead of
``ewoks`` for a real :term:`workflow`.

Re-producer side
----------------

Only ``ewoks`` itself is needed to recreate the environment of ``demo.json``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            uv init ewoks_reproducer
            uv add --project ewoks_reproducer ewoks
            uv run --project ewoks_reproducer ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: macOS

        .. code-block:: bash

            uv init ewoks_reproducer
            uv add --project ewoks_reproducer ewoks
            uv run --project ewoks_reproducer ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: Windows

        .. code-block:: powershell

            uv init ewoks_reproducer
            uv add --project ewoks_reproducer ewoks
            uv run --project ewoks_reproducer ewoks install demo.json --yes --env-root ewoks_envs

The environment of the :term:`workflow` is a uv project in ``ewoks_envs/demo`` with the
virtual environment in its ``.venv`` directory.

Execute the workflow
--------------------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            uv run --project ewoks_reproducer ewoks execute --env ewoks_envs/demo demo.json --outputs=all

    .. group-tab:: macOS

        .. code-block:: bash

            uv run --project ewoks_reproducer ewoks execute --env ewoks_envs/demo demo.json --outputs=all

    .. group-tab:: Windows

        .. code-block:: powershell

            uv run --project ewoks_reproducer ewoks execute --env ewoks_envs\demo demo.json --outputs=all

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
