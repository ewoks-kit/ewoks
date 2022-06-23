Ewoks events
============

Events can be emitted by *ewoks* during the execution of a workflow to notify
about progress and potential errors. For this you can specify one or more
destinations where the events should be send to.

To specify event handlers from python:

.. code:: python

    from ewoks import execute_graph

    execinfo = {
        "job_id": "1234",
        "handlers": [
            {
                "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
                "arguments": [{"name": "uri",
                               "value": "file:/tmp/ewoks_event.db"}],
            }
        ],
    }
    results = execute_graph("/path/to/file.json", execinfo=execinfo)

To specify event handlers from the command line:

.. code:: bash

    ewoks execute /path/to/file.json -j 1234 --sqlite3 /shared/path/test.db