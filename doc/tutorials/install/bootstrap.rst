.. _install_bootstrap:

Install without ewoks
=====================

``ewoks install`` needs a python environment with :term:`ewoks`. The ``ewoks-install``
script needs only a :term:`package manager`:

1. It creates a bootstrap environment with :term:`ewoks` and the engine that saved the
   :term:`workflow`.
2. It runs ``ewoks install`` in the bootstrap environment.

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

To try it with the demo :term:`workflow` of this documentation, download the workflow first

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            curl -LsSfO |docs_url|/demo.json
            curl -LsSf |docs_url|/ewoks-install.sh | sh -s -- demo.json

    .. group-tab:: macOS

        .. code-block:: bash

            curl -LsSfO |docs_url|/demo.json
            curl -LsSf |docs_url|/ewoks-install.sh | sh -s -- demo.json

    .. group-tab:: Windows

        .. code-block:: powershell

            irm |docs_url|/demo.json -OutFile demo.json
            & ([scriptblock]::Create((irm |docs_url|/ewoks-install.ps1))) demo.json

To read the script before you run it, download the script first

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            curl -LsSf -o ewoks-install.sh |docs_url|/ewoks-install.sh
            sh ewoks-install.sh demo.json

    .. group-tab:: macOS

        .. code-block:: bash

            curl -LsSf -o ewoks-install.sh |docs_url|/ewoks-install.sh
            sh ewoks-install.sh demo.json

    .. group-tab:: Windows

        .. code-block:: powershell

            irm |docs_url|/ewoks-install.ps1 -OutFile ewoks-install.ps1
            powershell -ExecutionPolicy Bypass -File ewoks-install.ps1 demo.json

Arguments
---------

.. code-block:: text

    ewoks-install.sh [OPTIONS] WORKFLOW [ARGS ...]

* ``WORKFLOW``: the first argument that is an existing file.
* ``ARGS``: the arguments of ``ewoks install``, for example ``--yes`` and ``--env-root``.
* ``OPTIONS`` and ``ARGS`` can be in any order.

Options of the script:

.. list-table::
    :widths: 35 65

    * - ``--bootstrap-requirement REQ``
      - Install ``REQ`` in the bootstrap environment instead of the ``bootstrap`` packages of
        the requirements, for example ``"ewoks>=7"`` or a wheel file. Repeat it for more
        packages, for example ``ewoksorange``.
    * - ``--bootstrap-dir DIR``
      - Directory of the bootstrap environments. Default: ``~/.ewoks/bootstrap``.
    * - ``--install-package-manager``
      - A flag without a value. Install the :term:`package manager` in
        ``DIR/package-managers`` when it is not installed, and pass its path to
        ``ewoks install``. Requires ``--package-manager-name``.
    * - ``-h``, ``--help``
      - Show the help of the script.

Options of the script and of ``ewoks install``:

.. list-table::
    :widths: 35 65

    * - ``--package-manager-name NAME``
      - The :term:`package manager` of the bootstrap environment and of the environment of the
        :term:`workflow`: ``uv``, ``pixi``, ``conda``, ``poetry`` or ``pip-venv``. Default:
        the first installed of uv, pixi, conda and poetry, else pip-venv.
    * - ``--package-manager-command COMMAND``
      - The command that runs the :term:`package manager`, for example ``python3.12`` for
        pip-venv. Requires ``--package-manager-name``.

For example, install uv when it is missing and do not ask for confirmation

.. code-block:: text

    ewoks-install.sh --install-package-manager --package-manager-name uv demo.json --yes

Select the package manager
--------------------------

One command for each :term:`package manager`. The commands install the
:term:`package manager` when it is missing.

.. tabs::

    .. group-tab:: Linux

        .. code-block:: bash

            curl -LsSf -o ewoks-install.sh |docs_url|/ewoks-install.sh
            sh ewoks-install.sh demo.json --package-manager-name pip-venv
            sh ewoks-install.sh demo.json --package-manager-name uv --install-package-manager
            sh ewoks-install.sh demo.json --package-manager-name pixi --install-package-manager
            sh ewoks-install.sh demo.json --package-manager-name conda --install-package-manager
            sh ewoks-install.sh demo.json --package-manager-name poetry --install-package-manager

    .. group-tab:: macOS

        .. code-block:: bash

            curl -LsSf -o ewoks-install.sh |docs_url|/ewoks-install.sh
            sh ewoks-install.sh demo.json --package-manager-name pip-venv
            sh ewoks-install.sh demo.json --package-manager-name uv --install-package-manager
            sh ewoks-install.sh demo.json --package-manager-name pixi --install-package-manager
            sh ewoks-install.sh demo.json --package-manager-name conda --install-package-manager
            sh ewoks-install.sh demo.json --package-manager-name poetry --install-package-manager

    .. group-tab:: Windows

        .. code-block:: powershell

            irm |docs_url|/ewoks-install.ps1 -OutFile ewoks-install.ps1
            powershell -ExecutionPolicy Bypass -File ewoks-install.ps1 demo.json --package-manager-name pip-venv
            powershell -ExecutionPolicy Bypass -File ewoks-install.ps1 demo.json --package-manager-name uv --install-package-manager
            powershell -ExecutionPolicy Bypass -File ewoks-install.ps1 demo.json --package-manager-name pixi --install-package-manager
            powershell -ExecutionPolicy Bypass -File ewoks-install.ps1 demo.json --package-manager-name conda --install-package-manager
            powershell -ExecutionPolicy Bypass -File ewoks-install.ps1 demo.json --package-manager-name poetry --install-package-manager

* pip-venv and poetry need a python interpreter on the machine. uv, pixi and conda do not.
* The script cannot install pip-venv: it is part of python.
* Conda cannot be installed in a directory with spaces.

The bootstrap environment
-------------------------

* The bootstrap environment only runs ``ewoks install``. It is not the environment of the
  :term:`workflow`.
* Its location is ``DIR/<package manager>/<name>``. The name contains the versions of the
  bootstrap packages and of python, for example ``ewoks=7.0.0@ewokscore=5.1.0@python=3.12``.
* The script uses the bootstrap environment again for a :term:`workflow` with the same
  versions.
* The script prints the ``ewoks install`` command before it runs it.
* ``ewoks install`` prints the python interpreter of the bootstrap environment, the command to
  run ``ewoks install`` again and the command to remove the bootstrap environment.
* When the script fails, it prints how to install without it.
