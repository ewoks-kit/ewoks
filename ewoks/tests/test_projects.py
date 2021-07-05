import pytest
import importlib


@pytest.mark.parametrize(
    "project", ["ewokscore", "ewoksdask", "ewoksppf", "ewoksorange"]
)
def test_import(project):
    importlib.import_module(project)
