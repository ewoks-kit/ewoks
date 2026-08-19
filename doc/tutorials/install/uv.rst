.. _install_uv:

uv
==

End-to-end walk-through with `uv <https://docs.astral.sh/uv/>`_.

Install uv
----------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            export UV_INSTALL_DIR=$HOME/.local/uv/bin
            curl -LsSf https://astral.sh/uv/install.sh | INSTALLER_NO_MODIFY_PATH=1 sh
            export PATH=$UV_INSTALL_DIR:$PATH

    .. group-tab:: macOS

        .. code-block:: bash

            export UV_INSTALL_DIR=$HOME/.local/uv/bin
            curl -LsSf https://astral.sh/uv/install.sh | INSTALLER_NO_MODIFY_PATH=1 sh
            export PATH=$UV_INSTALL_DIR:$PATH

    .. group-tab:: Windows

        .. code-block:: powershell

            $env:UV_INSTALL_DIR = "$env:USERPROFILE\.local\uv\bin"
            irm https://astral.sh/uv/install.ps1 | iex
            $env:PATH = "$env:UV_INSTALL_DIR;$env:PATH"

Producer side
-------------

Create an environment, install :term:`ewoks` in it and store a :term:`workflow` with the
packages of that environment as its ``requirements``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            uv venv ewoks_producer
            source ewoks_producer/bin/activate
            uv pip install ewoks
            ewoks convert demo demo.json --test
            deactivate

    .. group-tab:: macOS

        .. code-block:: bash

            uv venv ewoks_producer
            source ewoks_producer/bin/activate
            uv pip install ewoks
            ewoks convert demo demo.json --test
            deactivate

    .. group-tab:: Windows

        .. code-block:: powershell

            uv venv ewoks_producer
            ewoks_producer\Scripts\activate.ps1
            uv pip install ewoks
            ewoks convert demo demo.json --test
            deactivate

Install any package that provides :term:`tasks <Task>` instead of
``ewoks`` for a real :term:`workflow`.

Re-producer side
----------------

Only ``ewoks`` itself is needed to recreate the environment of ``demo.json``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            uv venv ewoks_reproducer
            source ewoks_reproducer/bin/activate
            uv pip install ewoks
            ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: macOS

        .. code-block:: bash

            uv venv ewoks_reproducer
            source ewoks_reproducer/bin/activate
            uv pip install ewoks
            ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: Windows

        .. code-block:: powershell

            uv venv ewoks_reproducer
            ewoks_reproducer\Scripts\activate.ps1
            uv pip install ewoks
            ewoks install demo.json --yes --env-root ewoks_envs

The environment of the :term:`workflow` is a uv project in ``ewoks_envs/demo`` with the
virtual environment in its ``.venv`` directory.

Execute the workflow
--------------------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            ewoks execute --env ewoks_envs/demo demo.json --outputs=all

    .. group-tab:: macOS

        .. code-block:: bash

            ewoks execute --env ewoks_envs/demo demo.json --outputs=all

    .. group-tab:: Windows

        .. code-block:: powershell

            ewoks execute --env ewoks_envs\demo demo.json --outputs=all

Clean up
--------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            deactivate
            rm -rf ewoks_producer ewoks_reproducer ewoks_envs demo.json

    .. group-tab:: macOS

        .. code-block:: bash

            deactivate
            rm -rf ewoks_producer ewoks_reproducer ewoks_envs demo.json

    .. group-tab:: Windows

        .. code-block:: powershell

            deactivate
            Remove-Item -Recurse -Force ewoks_producer, ewoks_reproducer, ewoks_envs, demo.json
