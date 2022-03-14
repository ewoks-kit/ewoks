Ewoks events
============

Execution events can be emitted by ewoks when event handlers are registered.

To register event handlers from python:

.. code:: python

    from ewoks import execute_graph

    execinfo = {
        "job_id": "1234",
        "handlers": [
            {
                "class": "ewokscore.events.handlers.EwoksSqlite3EventHandler",
                "arguments": [{"name": "uri",
                               "value": "file:/tmp/ewoks_event.db"}],
            }
        ],
    }
    results = execute_graph("/path/to/file.json", execinfo=execinfo)

To register event handlers from the shell:

.. code:: bash

    ewoks execute /path/to/file.json -j 1234 --sqlite3 /shared/path/test.db