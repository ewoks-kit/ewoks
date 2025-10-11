.. _hello_world:

Hello world
===========

This script demonstrates how to define an Ewoks workflow from the ground up. The only thing needed to run
it is the ``ewoks`` Python package

.. code-block:: bash

    pip install ewoks


The script defines defines two tasks, one that ask for a name and the other that creates a greeting, creates
a workflow out of these and executes it.

.. code-block:: python

    from ewokscore import Task
    from ewoks import execute_graph


    # Define a workflow task with an output
    class AskForName(Task, output_names=["input_name"]):
        def run(self):
            name = input("What is your name?")
            if not name:
                name = "World"
            self.outputs.input_name = name


    # Define a workflow task with inputs and outputs
    class SayHello(
        Task,
        input_names=["name"],
        optional_input_names=["in_french"],
        output_names=["greeting"],
    ):
        def run(self):
            name = self.inputs.name
            if self.inputs.in_french:
                hello = "Bonjour"
            else:
                hello = "Hello"
            self.outputs.greeting = f"{hello}, {name}!"


    # Define nodes: entities that will execute tasks
    nodes = [
        {
            "id": "ask_for_name",
            "task_type": "class",
            "task_identifier": "__main__.AskForName",
        },
        {
            "id": "say_hello",
            "task_type": "class",
            "task_identifier": "__main__.SayHello",
        },
    ]
    # Define links that make data flow from one node to another
    links = [
        {
            "source": "ask_for_name",
            "target": "say_hello",
            "data_mapping": [{"source_output": "input_name", "target_input": "name"}],
        }
    ]
    # Define a workflow from nodes, links and graph metadata
    workflow = {"graph": {"id": "hello_world"}, "nodes": nodes, "links": links}


    # Execute a workflow
    result = execute_graph(workflow)
    print(result)
    print('----')

    # Optionally, define inputs
    inputs = [{"id": "say_hello", "name": "in_french", "value": True}]

    # Execute a workflow with inputs
    result = execute_graph(workflow, inputs=inputs)
    print(result)

This is the output you should get

.. code-block:: bash

    $ python hello_world.py
    What is your name? Ewoks # <--- `input` waits for some input. `Ewoks` was typed here and Enter pressed.
    {'greeting': 'Hello, Ewoks!'}
    ----
    What is your name?  # <--- Enter was pressed without typing anything
    {'greeting': 'Bonjour, World!'}

.. note::

    Ewoks developers rarely design workflows by hand like this but instead use graphical interfaces to produce
    the dictionnary (usually stored in JSON). See :ref:`this page about the Ewoks graphical interfaces <gui>`.

.. note::

    For all the fields that can be set when creating the dictionnary representing the workflow, see the
    `Ewoks specification <https://ewokscore.readthedocs.io/en/latest/reference/specs.html>`_.
