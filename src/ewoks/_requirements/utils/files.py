import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict
from typing import Generator
from typing import Mapping


def write_files(directory: Path, files: Mapping[str, str]) -> None:
    """Write files, relative to a directory that is created when missing."""
    for name, content in files.items():
        filename = directory / name
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(content, encoding="utf-8")


def read_files(directory: Path, *names: str) -> Dict[str, str]:
    """Read files, relative to a directory, skipping the ones that do not exist."""
    files = {}
    for name in names:
        try:
            files[name] = (directory / name).read_text(encoding="utf-8")
        except OSError:
            continue
    return files


@contextmanager
def temporary_files(files: Mapping[str, str]) -> Generator[Path, None, None]:
    """Write files in a temporary directory which is yielded."""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        write_files(path, files)
        yield path
