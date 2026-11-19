.. _install_pip_venv:

pip and venv
============

End-to-end walk-through with ``pip`` and ``venv``. Both are part of a python installation, so
there is no other :term:`package manager` to install.

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
packages of that environment as its ``requirements``.

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            python3 -m venv ewoks_producer
            source ewoks_producer/bin/activate
            pip install ewoks
            ewoks convert demo demo.json --test
            deactivate

    .. group-tab:: macOS

        .. code-block:: bash

            python3 -m venv ewoks_producer
            source ewoks_producer/bin/activate
            pip install ewoks
            ewoks convert demo demo.json --test
            deactivate

    .. group-tab:: Windows

        .. code-block:: powershell

            py -m venv ewoks_producer
            ewoks_producer\Scripts\Activate.ps1
            pip install ewoks
            ewoks convert demo demo.json --test
            deactivate

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

            python3 -m venv ewoks_reproducer
            source ewoks_reproducer/bin/activate
            pip install ewoks
            ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: macOS

        .. code-block:: bash

            python3 -m venv ewoks_reproducer
            source ewoks_reproducer/bin/activate
            pip install ewoks
            ewoks install demo.json --yes --env-root ewoks_envs

    .. group-tab:: Windows

        .. code-block:: powershell

            py -m venv ewoks_reproducer
            ewoks_reproducer\Scripts\Activate.ps1
            pip install ewoks
            ewoks install demo.json --yes --env-root ewoks_envs

The environment of the :term:`workflow` is a virtual environment in ``ewoks_envs/demo``.

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
