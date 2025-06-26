import asyncio
import os
import sys
from typing import Generator

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest
import testbook
from testbook.client import TestbookNotebookClient

_ROOT_DIR = os.path.join(os.path.dirname(__file__), "notebooks")
_NOTEBOOKS = {"running_workflows.ipynb": "result = 16"}


@pytest.mark.parametrize("filename", _NOTEBOOKS)
def test_notebooks(filename):
    expected_output = _NOTEBOOKS[filename]
    filename = os.path.join(_ROOT_DIR, filename)

    decorator = testbook.testbook(filename)

    output_found = False

    def verify_notebook(tb: TestbookNotebookClient) -> None:
        tb.execute()

        nonlocal output_found
        for output in _iter_cell_output(tb):
            print(output)
            if expected_output in output:
                output_found = True
                break

    decorator(verify_notebook)()

    assert output_found


def _iter_cell_output(tb: TestbookNotebookClient) -> Generator[str, None, None]:
    for cell in tb.nb.cells:
        output_nodes = cell.get("outputs", [])
        for output_node in output_nodes:
            if output_node["output_type"] == "stream":
                yield output_node["text"]
