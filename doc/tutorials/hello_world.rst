Hello world
===========

A short script that defines a task, creates a workflow and executes it.

.. code:: python

    from ewokscore import Task
    from ewokscore import load_graph

    # Implement a workflow task
    class SumTask(
        Task, input_names=["a"], optional_input_names=["b"], output_names=["result"]
    ):
        def run(self):
            result = self.inputs.a
            if self.inputs.b:
                result += self.inputs.b
            self.outputs.result = result


    # Define a workflow
    nodes = [
        {
            "id": "task1",
            "task_type": "class",
            "task_identifier": "__main__.SumTask",
            "default_inputs": [{"name": "a", "value": 1}],
        },
        {
            "id": "task2",
            "task_type": "class",
            "task_identifier": "__main__.SumTask",
            "default_inputs": [{"name": "b", "value": 1}],
        },
        {
            "id": "task3",
            "task_type": "class",
            "task_identifier": "__main__.SumTask",
            "default_inputs": [{"name": "b", "value": 1}],
        },
    ]
    links = [
        {
            "source": "task1",
            "target": "task2",
            "data_mapping": [{"target_input": "a", "source_output": "result"}],
        },
        {
            "source": "task2",
            "target": "task3",
            "data_mapping": [{"target_input": "a", "source_output": "result"}],
        },
    ]
    workflow = {"nodes": nodes, "links": links}

    # Execute a workflow (without task scheduler)
    graph = load_graph(workflow)
    varinfo = {"root_uri": "/tmp/myresults"}  # optional
    tasks = graph.execute(varinfo=varinfo)
    print(tasks["task3"].output_values)
