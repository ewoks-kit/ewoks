Job scheduling
==============

The client may want to start a workflow execution remotely and wait for the result
while doing other work.

Install on the client side

.. code:: bash

    python3 -m pip install ewoksjob[redis]

Install on the worker side

.. code:: bash

    python3 -m pip install ewoksjob[worker,redis,monitor]

The communication between client and worker goes through *Redis*, *RabbitMQ* or *Sqlite3*.
Depending on which one you choose, the `redis` installation option may vary. Both client and
worker need access to a configuration that specifies the URL of the database and/or broker.
For more information see the `ewoksjob documentation <https://ewoksjob.readthedocs.io/>`_.

Start a worker that can execute *ewoks* graphs

.. code:: bash

    celery -A ewoksjob.apps.ewoks worker

Start a workflow from python, possible from another machine

.. code:: python

    from ewoksjob.client import submit

    workflow = {"graph": {"id": "mygraph"}}
    future = submit(args=(workflow,))
    result = future.get()

Start a web server for monitoring jobs

.. code:: bash

    flower
