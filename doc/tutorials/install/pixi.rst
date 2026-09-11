.. _install_pixi:

pixi
====

End-to-end walk-through of `workflow installation and execution <../install.rst>`_
with `pixi <https://pixi.sh/>`_.

Pixi works with workspaces instead of environments: its commands need a directory with a
``pixi.toml`` file, selected with ``--manifest-path``. Like conda it installs python itself
and it takes its packages from the conda channels, with the packages of the python package
index in a section of their own.

Install pixi
------------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            export PIXI_HOME=$HOME/.pixi  # default location
            export PIXI_NO_PATH_UPDATE=true
            curl -fsSL https://pixi.sh/install.sh | sh
            export PATH=$PIXI_HOME/bin:$PATH

    .. group-tab:: macOS

        .. code-block:: bash

            export PIXI_HOME=$HOME/.pixi  # default location
            export PIXI_NO_PATH_UPDATE=true
            curl -fsSL https://pixi.sh/install.sh | sh
            export PATH=$PIXI_HOME/bin:$PATH

    .. group-tab:: Windows

        .. code-block:: powershell

            $env:PIXI_HOME = "$env:USERPROFILE\.pixi"  # default location
            $env:PIXI_NO_PATH_UPDATE = "true"
            irm -useb https://pixi.sh/install.ps1 | iex
            $env:PATH = "$env:PIXI_HOME\bin;$env:PATH"

Producer side
-------------

Create a workspace, install :term:`ewoks` in it and store a :term:`workflow` with the packages
of that workspace as its ``requirements``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            pixi init ewoks_producer
            pixi add --manifest-path ewoks_producer/pixi.toml python pip
            pixi add --manifest-path ewoks_producer/pixi.toml --pypi ewoks
            pixi run --manifest-path ewoks_producer/pixi.toml ewoks convert demo demo.json --test

    .. group-tab:: macOS

        .. code-block:: bash

            pixi init ewoks_producer
            pixi add --manifest-path ewoks_producer/pixi.toml python pip
            pixi add --manifest-path ewoks_producer/pixi.toml --pypi ewoks
            pixi run --manifest-path ewoks_producer/pixi.toml ewoks convert demo demo.json --test

    .. group-tab:: Windows

        .. code-block:: powershell

            pixi init ewoks_producer
            pixi add --manifest-path ewoks_producer\pixi.toml python pip
            pixi add --manifest-path ewoks_producer\pixi.toml --pypi ewoks
            pixi run --manifest-path ewoks_producer\pixi.toml ewoks convert demo demo.json --test

Install any package that provides :term:`tasks <Task>` instead of
``ewoks`` for a real :term:`workflow`. ``pixi run`` executes in the current directory, so the
workflow paths are relative to it and not to the workspace.

Re-producer side
----------------

Only ``ewoks`` itself is needed to recreate the environment of ``demo.json``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            pixi init ewoks_reproducer
            pixi add --manifest-path ewoks_reproducer/pixi.toml python pip
            pixi add --manifest-path ewoks_reproducer/pixi.toml --pypi ewoks
            pixi run --manifest-path ewoks_reproducer/pixi.toml ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: macOS

        .. code-block:: bash

            pixi init ewoks_reproducer
            pixi add --manifest-path ewoks_reproducer/pixi.toml python pip
            pixi add --manifest-path ewoks_reproducer/pixi.toml --pypi ewoks
            pixi run --manifest-path ewoks_reproducer/pixi.toml ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: Windows

        .. code-block:: powershell

            pixi init ewoks_reproducer
            pixi add --manifest-path ewoks_reproducer\pixi.toml python pip
            pixi add --manifest-path ewoks_reproducer\pixi.toml --pypi ewoks
            pixi run --manifest-path ewoks_reproducer\pixi.toml ewoks install demo.json --yes --env-root ewoks_envs

The environment of the :term:`workflow` is a pixi workspace in ``ewoks_envs/demo`` with the
environment in its ``.pixi/envs/default`` directory.

Execute the workflow
--------------------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            pixi run --manifest-path ewoks_reproducer/pixi.toml ewoks execute --env ewoks_envs/demo demo.json --outputs=all

    .. group-tab:: macOS

        .. code-block:: bash

            pixi run --manifest-path ewoks_reproducer/pixi.toml ewoks execute --env ewoks_envs/demo demo.json --outputs=all

    .. group-tab:: Windows

        .. code-block:: powershell

            pixi run --manifest-path ewoks_reproducer\pixi.toml ewoks execute --env ewoks_envs\demo demo.json --outputs=all

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
