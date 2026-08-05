.. _cli:

CLI reference
=============

ewoks install
-------------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: install

    Install the packages required to run a :term:`workflow`.
    
    **ewoks install** relies on the existence of the ``requirements`` field in the ``graph`` field of the :term:`workflow`.

    If no ``requirements`` field exist, **ewoks install** will try to extract requirements from the :term:`tasks <Task>` in the :term:`workflows <Workflow>` before installing them.

    Unless ``--yes`` is provided, **ewoks install** will ask for confirmation before installing the packages.

    By default, packages are installed in the current Python environment: if **ewoks install** is run in a virtual environment, the packages will be installed in this virtual environment.

ewoks convert
-------------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: convert

    Convert a source :term:`workflow` in another format supported by :term:`Ewoks`.
    
    The source :term:`workflow` is untouched: a new destination :term:`workflow` is created.

    .. important::

        **ewoks convert** will save the packages installed in the current environment as ``requirements`` in the destination :term:`workflow`.
        
        ⚠️ If the source :term:`workflow` has a ``requirements`` field, it will therefore be replaced by this package list.

        This can be disabled by using the ``--exclude-requirements`` argument.
    
    **ewoks convert** can also be used to store ``inputs`` inside the destination :term:`workflow`.

ewoks execute
-------------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: execute

    Execute a :term:`workflow` using one of the :term:`execution engines <Execution engine>` supported by :term:`Ewoks`.
    
    The :term:`workflow` can have any format as long it is supported by :term:`Ewoks`.

    Inputs can be provided only for this execution.

    .. tip::
        
        Using the execution option ``convert_destination`` (``-o convert_destination=<new_workflow_name>``) runs ``ewoks convert`` on the executed :term:`workflow`, producing a new :term:`workflow` that stored the inputs and the requirements inside.

        The produced :term:`workflow` can then be used as a provenance document since it can reproduce the source :term:`workflow` execution in exactly the same way.

ewoks submit
------------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: submit

    Execute a :term:`workflow` remotely, in a :term:`worker`.
    
    Very similar to ``ewoks execute`` except the execution does not run in this environment (client) but in a remote one (:term:`worker`).

    Requires the ``EWOKS_CONFIG_URI`` environment variable to be set.

    .. tip:: 

        Before running this command, the client and the :term:`worker` must have agreed on a messaging protocol to communicate.
        
        See the `ewoksjob documentation <https://ewoksjob.readthedocs.io>`_ to see how to set-up this.

ewoks show
----------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: show

    Display the :term:`workflow` parameters with their default values and descriptions.

    Required parameters without default value are highlighted. Parameters which get their value at runtime from upstream :term:`nodes` in the :term:`workflow` are not shown.

    Parameters values in the displayed table can be provided in the same way as inputs for ``ewoks execute``.

ewoks lint
----------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: lint

    **Checks if a workflow is conform to the Ewoks specification**.

    Validation errors will be printed in the console if any.
