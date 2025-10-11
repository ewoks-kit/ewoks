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

    **Install the packages required to run a workflow**. 
    
    **ewoks install** relies on the existence of the ``requirements`` field in the ``graph`` field of the workflow.

    If no ``requirements`` field exist, **ewoks install** will try to extract requirements from the tasks in the workflows before installing them.

    Unless ``--yes`` is provided, **ewoks install** will ask for confirmation before installing the packages.

    By default, packages are installed in the current Python environment: if **ewoks install** is run in a virtual environment, the packages will be installed in this virtual environment.

ewoks convert
-------------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: convert

    **Convert a source workflow in another format supported by Ewoks**. 
    
    The source workflow is untouched: a new destination workflow is created.

    .. important::

        **ewoks convert** will save the packages installed in the current environment as `requirements` in the destination workflow. 
        
        ⚠️ If the source workflow has a `requirements` field, it will therefore be replaced by this package list.

        This can be disabled by using the ``--exclude-requirements`` argument.
    
    **ewoks convert** can also be used to store `inputs` inside the destination workflow.

ewoks execute
-------------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: execute

    **Execute a workflow using one of the Ewoks-supported engine**. 
    
    The workflow can have any format as long it is supported by Ewoks.

    Inputs can be provided only for this execution.

    .. tip::
        
        Using the execution option ``convert_destination`` (``-o convert_destination=<new_workflow_name>``) runs `ewoks convert`  on the executed workflow, producing a new workflow that stored the inputs and the requirements inside.

        The produced workflow can then be used as a provenance document since it can reproduce the source workflow execution in exactly the same way.

ewoks submit
------------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: submit

    **Execute a workflow remotely, in a worker**. 
    
    Very similar to ``ewoks execute`` except the execution does not run in this environment (client) but in a remote one (worker).

    Requires the `EWOKS_CONFIG_URI` environment variable to be set.

    .. tip:: 

        Before running this command, the client and the worker must have agreed on a messaging protocol to communicate. 
        
        See the `ewoksjob documentation <https://ewoksjob.readthedocs.io>`_ to see how to set-up this.

ewoks show
----------

.. argparse::
    :module: ewoks.__main__
    :func: create_argument_parser
    :prog: ewoks
    :path: show

    **Display the workflow parameters with their default values and descriptions**.

    Required parameters without default value are highlighted. Parameters which get their value at runtime from upstream nodes in the workflow are not shown.

    Parameters values in the displayed table can be provided in the same way as inputs for ``ewoks execute``.
