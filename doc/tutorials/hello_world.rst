Hello world
===========

A short script that defines a task, creates a workflow and executes it.

.. code:: python

    from ewokscore import Task
    from ewoks import execute_graph

    # Implement a workflow task
    class SumTask(
        Task, input_names=["a"], optional_input_names=["b"], output_names=["result"]
    ):
        def run(self):
            result = self.inputs.a
            if self.inputs.b:
                result += self.inputs.b
            self.outputs.result = result


    # Define a workflow with default inputs
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
            "data_mapping": [{"source_output": "result", "target_input": "a"}],
        },
        {
            "source": "task2",
            "target": "task3",
            "data_mapping": [{"source_output": "result", "target_input": "a"}],
        },
    ]
    workflow = {"graph": {"id": "testworkflow"}, "nodes": nodes, "links": links}

    # Define task inputs
    inputs = [{"id": "task1", "name": "a", "value": 10}]

    # Execute a workflow (use a proper Ewoks task scheduler in production)
    varinfo = {"root_uri": "/tmp/myresults"}  # optionally save all task outputs
    result = execute_graph(workflow, varinfo=varinfo, inputs=inputs)
    print(result)
