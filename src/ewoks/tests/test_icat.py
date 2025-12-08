from ..bindings import execute_graph


def test_upload_context(mock_icat_client):
    graph = {
        "graph": {"id": "demo", "label": "demo", "schema_version": "1.1"},
        "links": [],
        "nodes": [
            {
                "default_inputs": [
                    {"name": "a", "value": 42},
                    {"name": "delay", "value": 0},
                ],
                "id": "task0",
                "task_identifier": "ewokscore.tests.examples.tasks.sumtask.SumTask",
                "task_type": "class",
            },
        ],
    }

    execute_graph(
        graph,
        inputs=[{"name": "delay", "value": 0, "all": False}],
        upload_parameters={},
    )

    args, kwargs = mock_icat_client.return_value.store_processed_data.call_args

    assert not args
    assert set(kwargs) == {"metadata"}
    assert set(kwargs["metadata"]) == {"startDate", "endDate"}
    duration = kwargs["metadata"]["endDate"] - kwargs["metadata"]["startDate"]

    delay = 1
    margin = 0.5

    execute_graph(
        graph,
        inputs=[{"name": "delay", "value": delay + margin, "all": False}],
        upload_parameters={},
    )

    args, kwargs = mock_icat_client.return_value.store_processed_data.call_args

    assert not args
    assert set(kwargs) == {"metadata"}
    assert set(kwargs["metadata"]) == {"startDate", "endDate"}
    duration_with_delay = (
        kwargs["metadata"]["endDate"] - kwargs["metadata"]["startDate"]
    )

    difference = duration_with_delay - duration
    assert difference.total_seconds() > delay
