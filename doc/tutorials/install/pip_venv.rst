.. _install_pip_venv:

pip and venv
============

End-to-end walk-through with ``pip`` and ``venv``. Both are part of a python installation, so
there is no other :term:`package manager` to install.

Producer side
-------------

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

Install any package that provides :term:`tasks <Task>` instead of
``ewoks`` for a real :term:`workflow`.

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
