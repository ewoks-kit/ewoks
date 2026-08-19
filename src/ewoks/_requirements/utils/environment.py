import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from typing import Tuple
from typing import Union

from . import process

logger = logging.getLogger(__name__)

ENVIRONMENT_SUBDIRS: Tuple[str, ...] = (
    "",  # environment prefix, for example created by `python -m venv`
    ".venv",  # uv project
)


@dataclass(frozen=True)
class Environment:
    """Python environment a package manager creates, installs into and runs."""

    location: Path
    """Directory provided by the user: an environment prefix or a project."""

    python: Path
    """Python interpreter of the environment."""

    @classmethod
    def current(cls) -> "Environment":
        """Environment of the running python interpreter."""
        return cls(location=Path(sys.prefix), python=Path(sys.executable))

    @classmethod
    def at_location(cls, location: Union[str, Path], subdir: str = "") -> "Environment":
        """Environment with a prefix at a fixed position inside the location."""
        location = Path(os.path.abspath(location))
        prefix = location / subdir if subdir else location
        return cls(location=location, python=python_executable(prefix))

    @classmethod
    def from_location(cls, location: Union[str, Path]) -> "Environment":
        """Environment found inside the location.

        :raises ValueError: no python interpreter found
        """
        for subdir in ENVIRONMENT_SUBDIRS:
            environment = cls.at_location(location, subdir)
            if environment.python.is_file():
                return environment
        raise ValueError(f"No python environment found in '{location}'")

    @property
    def prefix(self) -> Path:
        """Environment prefix, which is the location itself unless the package
        manager creates the environment inside the location.
        """
        directory = self.python.parent
        if directory.name in ("bin", "Scripts"):
            return directory.parent
        return directory

    def exists(self) -> bool:
        return self.python.is_file()

    def python_version(self) -> str:
        """
        :raises RuntimeError: environment has no python interpreter
        """
        return interpreter_version(self.python)

    def distribution_version(self, name: str) -> Optional[str]:
        """Returns None when the distribution is not installed.

        :raises RuntimeError: environment has no python interpreter
        """
        code = (
            "import importlib.metadata as m\n"
            f"try: print(m.version({name!r}))\n"
            "except m.PackageNotFoundError: pass"
        )
        return self._python_output(code) or None

    def _python_output(self, code: str) -> str:
        return process.check_output(self.python, "-c", code).strip()


def python_executable(prefix: Path) -> Path:
    """Python interpreter of an environment prefix. The interpreter of a virtual
    environment is returned when the environment does not exist yet.
    """
    relative_paths = _interpreters()
    for relative in relative_paths:
        python = prefix / relative
        if python.is_file():
            return python
    return prefix / relative_paths[0]


def _interpreters() -> Tuple[Path, ...]:
    """Interpreter locations inside an environment prefix, the first one being where
    a virtual environment has it. On Windows an environment that is not virtual (a
    python installation) has it in the prefix itself.
    """
    if sys.platform == "win32":
        return (Path("Scripts", "python.exe"), Path("python.exe"))
    return (Path("bin", "python"),)


def interpreter_version(python: Union[str, Path]) -> str:
    """Version of a python interpreter.

    :raises RuntimeError: not a python interpreter
    """
    return process.check_output(
        python, "-c", "import platform; print(platform.python_version())"
    ).strip()


def create_venv(
    base_python: Union[str, Path], prefix: Path, python_version: Optional[str] = None
) -> None:
    """Create a virtual environment with the `venv` module, which cannot provide
    another python version than the one of the interpreter that creates it.

    :raises RuntimeError: creation failed
    """
    if python_version:
        base_version = interpreter_version(base_python)
        if python_version != base_version:
            logger.warning(
                "'venv' cannot provide python %s: creating the environment with "
                "python %s instead",
                python_version,
                base_version,
            )
    process.check_call(base_python, "-m", "venv", prefix)
