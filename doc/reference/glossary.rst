Glossary
--------

.. glossary:: 
    :sorted:

    Ewoks
        Ewoks is an extensible meta :term:`workflow` system which supports executing :term:`workflows <Workflow>` on different :term:`execution engines <Execution engine>`. Ewoks can be extended to support new :term:`execution engines <Execution engine>`. Ewoks currently supports 4 :term:`workflow` :term:`execution engines <Execution engine>`.

    Ewoksweb
        Ewoksweb is a web application for editing and executing :term:`Ewoks` :term:`workflows <Workflow>` in a web browser.

    Links
        Links are unidirectional relationships between two :term:`Nodes` to be able to sequence their execution and pass data between the nodes.

    Nodes
        Nodes are the representation of :term:`tasks <Task>` in :term:`Ewoks` :term:`workflows <Workflow>`. They can have 1 or more input and output parameters. Input and output parameters can be required or optional.

    Task
        Tasks implement :term:`Nodes`. Tasks can be impemented in a variety of ways e.g. as a python function, jupyter notebook, or script.

    Worker
        A worker is an implementation of a process capable of executing :term:`Ewoks` :term:`workflows <Workflow>`, either locally or remotely by submitting them to a batch scheduler.

    Workflow
        A workflow is a sequence of high level steps for processing data or controlling hardware. Workflows are presented as a graph of :term:`Nodes` and :term:`Links`.

    Execution engine
        An execution engine is the underlying software used to execute the :term:`workflow`. :term:`Ewoks` supports multiple execution engines: pypushflow, orange, dask and the ewoks internal excution engine.

    Package manager
        A package manager creates python environments and installs packages in them. :term:`Ewoks` uses package managers to store the environment in which a :term:`workflow` was created and to recreate it: pip with venv, uv and pixi.

    blissdata
        `Blissdata <https://bliss.gitlab-pages.esrf.fr/blissdata>`_ is an API for accessing data from BLISS in memory.
