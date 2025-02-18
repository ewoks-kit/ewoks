import importlib

import pytest


@pytest.mark.parametrize(
    "project", ["ewokscore", "ewoksdask", "ewoksppf", "ewoksorange"]
)
def test_import(project):
    importlib.import_module(project)
