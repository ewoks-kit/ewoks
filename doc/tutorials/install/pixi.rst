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

Create a workspace, install :term:`ewoks` and ``mytasks`` in it and store your :term:`workflow`
with the packages of that workspace as its ``requirements``

* ``mytasks``: the packages that provide the :term:`tasks <Task>` of your :term:`workflow`.
* ``myworkflow.json``: your :term:`workflow`. See :doc:`how to create a workflow <../create_workflow>`.

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            pixi init ewoks_producer
            pixi add --manifest-path ewoks_producer/pixi.toml python pip
            pixi add --manifest-path ewoks_producer/pixi.toml --pypi ewoks mytasks
            pixi run --manifest-path ewoks_producer/pixi.toml ewoks convert myworkflow.json myworkflow_requirements.json

    .. group-tab:: macOS

        .. code-block:: bash

            pixi init ewoks_producer
            pixi add --manifest-path ewoks_producer/pixi.toml python pip
            pixi add --manifest-path ewoks_producer/pixi.toml --pypi ewoks mytasks
            pixi run --manifest-path ewoks_producer/pixi.toml ewoks convert myworkflow.json myworkflow_requirements.json

    .. group-tab:: Windows

        .. code-block:: powershell

            pixi init ewoks_producer
            pixi add --manifest-path ewoks_producer\pixi.toml python pip
            pixi add --manifest-path ewoks_producer\pixi.toml --pypi ewoks mytasks
            pixi run --manifest-path ewoks_producer\pixi.toml ewoks convert myworkflow.json myworkflow_requirements.json

Re-producer side
----------------

Only ``ewoks`` itself is needed to recreate the environment of ``demo.json``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            pixi init ewoks_reproducer
            pixi add --manifest-path ewoks_reproducer/pixi.toml python pip
            pixi add --manifest-path ewoks_reproducer/pixi.toml --pypi ewoks
            pixi run --manifest-path ewoks_reproducer/pixi.toml ewoks install demo.json --yes --env-root /tmp/ewoks_envs

    .. group-tab:: macOS

        .. code-block:: bash

            pixi init ewoks_reproducer
            pixi add --manifest-path ewoks_reproducer/pixi.toml python pip
            pixi add --manifest-path ewoks_reproducer/pixi.toml --pypi ewoks
            pixi run --manifest-path ewoks_reproducer/pixi.toml ewoks install demo.json --yes --env-root /tmp/ewoks_envs

    .. group-tab:: Windows

        .. code-block:: powershell

            pixi init ewoks_reproducer
            pixi add --manifest-path ewoks_reproducer\pixi.toml python pip
            pixi add --manifest-path ewoks_reproducer\pixi.toml --pypi ewoks
            pixi run --manifest-path ewoks_reproducer\pixi.toml ewoks install demo.json --yes --env-root "$env:TEMP\ewoks_envs"

The environment of the :term:`workflow` is a pixi workspace in ``/tmp/ewoks_envs/demo`` (``$env:TEMP\ewoks_envs\demo`` on Windows) with the
environment in its ``.pixi/envs/default`` directory.

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

            pixi run --manifest-path ewoks_reproducer/pixi.toml ewoks execute --env /tmp/ewoks_envs/demo demo.json --outputs=all

    .. group-tab:: macOS

        .. code-block:: bash

            pixi run --manifest-path ewoks_reproducer/pixi.toml ewoks execute --env /tmp/ewoks_envs/demo demo.json --outputs=all

    .. group-tab:: Windows

        .. code-block:: powershell

            pixi run --manifest-path ewoks_reproducer\pixi.toml ewoks execute --env "$env:TEMP\ewoks_envs\demo" demo.json --outputs=all

Clean up
--------

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            rm -rf ewoks_producer ewoks_reproducer /tmp/ewoks_envs demo.json

    .. group-tab:: macOS

        .. code-block:: bash

            rm -rf ewoks_producer ewoks_reproducer /tmp/ewoks_envs demo.json

    .. group-tab:: Windows

        .. code-block:: powershell

            Remove-Item -Recurse -Force ewoks_producer, ewoks_reproducer, "$env:TEMP\ewoks_envs", demo.json
