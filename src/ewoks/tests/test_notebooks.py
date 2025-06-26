import asyncio
import sys
from typing import Generator

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest
import testbook
from testbook.client import TestbookNotebookClient

from .notebooks import notebook_path

_NOTEBOOK_OUTPUTS = {"running_workflows.ipynb": "result = 16"}


@pytest.mark.parametrize("name", _NOTEBOOK_OUTPUTS)
def test_notebooks(name):
    expected_output = _NOTEBOOK_OUTPUTS[name]
    with notebook_path(name) as filename:
        decorator = testbook.testbook(filename)

        output_found = False

        def verify_notebook(tb: TestbookNotebookClient) -> None:
            tb.execute()

            nonlocal output_found
            for output in _iter_cell_outputs(tb):
                print(output)
                if expected_output in output:
                    output_found = True
                    break

        decorator(verify_notebook)()

        assert output_found


def _iter_cell_outputs(tb: TestbookNotebookClient) -> Generator[str, None, None]:
    for cell in tb.nb.cells:
        output_nodes = cell.get("outputs", [])
        for output_node in output_nodes:
            if output_node["output_type"] == "stream":
                yield output_node["text"]
