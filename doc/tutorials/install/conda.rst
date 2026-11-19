.. _install_conda:

conda
=====

End-to-end walk-through with `conda <https://docs.conda.io/>`_. Conda installs python itself,
so the environment of a :term:`workflow` can have another python version than the one that
recreates it.

Install conda
-------------

`Miniforge <https://github.com/conda-forge/miniforge>`_ is a conda installation configured
with the conda-forge channel

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            export CONDA_ROOT=$HOME/miniforge3
            curl -LsSf -o /tmp/miniforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
            bash /tmp/miniforge.sh -b -p $CONDA_ROOT
            source $CONDA_ROOT/etc/profile.d/conda.sh

    .. group-tab:: macOS

        .. code-block:: bash

            export CONDA_ROOT=$HOME/miniforge3
            curl -LsSf -o /tmp/miniforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
            bash /tmp/miniforge.sh -b -p $CONDA_ROOT
            source $CONDA_ROOT/etc/profile.d/conda.sh

    .. group-tab:: Windows

        .. code-block:: powershell

            $env:CONDA_ROOT = "$env:USERPROFILE\miniforge3"
            irm https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe -OutFile miniforge.exe
            Start-Process -Wait -FilePath .\miniforge.exe -ArgumentList "/S", "/D=$env:CONDA_ROOT"
            & "$env:CONDA_ROOT\shell\condabin\conda-hook.ps1"

Producer side
-------------

A :term:`workflow` with requirements comes from one of three sources.

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

Generate the demo workflow
++++++++++++++++++++++++++

Create an environment, install :term:`ewoks` in it and store a :term:`workflow` with the
packages of that environment as its ``requirements``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            conda create --yes --prefix ewoks_producer python pip
            conda activate ./ewoks_producer
            pip install ewoks
            ewoks convert demo demo.json --test
            conda deactivate

    .. group-tab:: macOS

        .. code-block:: bash

            conda create --yes --prefix ewoks_producer python pip
            conda activate ./ewoks_producer
            pip install ewoks
            ewoks convert demo demo.json --test
            conda deactivate

    .. group-tab:: Windows

        .. code-block:: powershell

            conda create --yes --prefix ewoks_producer python pip
            conda activate .\ewoks_producer
            pip install ewoks
            ewoks convert demo demo.json --test
            conda deactivate

Generate your own workflow
++++++++++++++++++++++++++

Install the packages that provide the :term:`tasks <Task>` of your :term:`workflow` instead of
``ewoks``, and :doc:`create <../create_workflow>` ``myworkflow.json`` with them.
Then store its requirements

.. code-block:: bash

    ewoks convert myworkflow.json myworkflow_requirements.json

Re-producer side
----------------

Only ``ewoks`` itself is needed to recreate the environment of ``demo.json``

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            conda create --yes --prefix ewoks_reproducer python pip
            conda activate ./ewoks_reproducer
            pip install ewoks
            ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: macOS

        .. code-block:: bash

            conda create --yes --prefix ewoks_reproducer python pip
            conda activate ./ewoks_reproducer
            pip install ewoks
            ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: Windows

        .. code-block:: powershell

            conda create --yes --prefix ewoks_reproducer python pip
            conda activate .\ewoks_reproducer
            pip install ewoks
            ewoks install demo.json --yes --env-root ewoks_envs

The environment of the :term:`workflow` is a conda environment in ``ewoks_envs/demo``. Without
``--env-root`` it is created in the first environment directory of conda, where
``conda activate demo`` finds it.

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

            conda deactivate
            rm -rf ewoks_producer ewoks_reproducer ewoks_envs demo.json

    .. group-tab:: macOS

        .. code-block:: bash

            conda deactivate
            rm -rf ewoks_producer ewoks_reproducer ewoks_envs demo.json

    .. group-tab:: Windows

        .. code-block:: powershell

            conda deactivate
            Remove-Item -Recurse -Force ewoks_producer, ewoks_reproducer, ewoks_envs, demo.json

.. note::

    ``mamba`` and ``micromamba`` are faster implementations of conda. Use
    ``--package-manager-command micromamba`` to let ``ewoks install`` invoke one of them.
