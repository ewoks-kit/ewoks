import os
from glob import glob
import pytest
import testbook

root_dir = os.path.join(os.path.dirname(__file__), "notebooks")
notebooks = [os.path.basename(f) for f in glob(os.path.join(root_dir, "*.ipynb"))]


@pytest.mark.parametrize("filename", notebooks)
def test_notebooks(filename):
    filename = os.path.join(root_dir, filename)
    with testbook.testbook(filename, execute=True):
        pass
