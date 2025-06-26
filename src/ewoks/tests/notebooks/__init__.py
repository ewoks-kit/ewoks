import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

if sys.version_info < (3, 9):
    import importlib_resources
else:
    import importlib.resources as importlib_resources


@contextmanager
def notebook_path(*args) -> Generator[Path, None, None]:
    source = importlib_resources.files(__name__).joinpath(*args)
    with importlib_resources.as_file(source) as path:
        if not path.is_file():
            raise FileNotFoundError(f"Not a file: '{source}'")
        yield path
