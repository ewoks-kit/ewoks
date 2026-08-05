"""Package manager specific knowledge needed by the package manager tests.

Add a `ManagerCase` to `MANAGER_CASES` to include a package manager in the
tests that apply to all package managers.
"""

import subprocess
import sys
from pathlib import Path
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

import pytest

from ..._requirements.pip import PipManager
from ..._requirements.utils.base_manager import BaseManager
from ..._requirements.utils.freeze_manager import FreezeManager
from ..._requirements.uv import UvManager


class Environment:
    """Python environment to gather requirements from or install requirements in."""

    def __init__(self, path: Path) -> None:
        self.path = path

    @property
    def python(self) -> str:
        if sys.platform == "win32":
            return str(self.path / "Scripts" / "python.exe")
        return str(self.path / "bin" / "python")

    def get_version(self, name: str) -> str:
        """
        :raises RuntimeError: distribution is not installed
        """
        code = f"import importlib.metadata; print(importlib.metadata.version({name!r}))"
        try:
            output = subprocess.check_output(  # noqa: S603 - Trusted test command;
                [self.python, "-c", code], text=True, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            raise RuntimeError(f"{name} package is not installed") from None
        return output.strip()


class ManagerCase:
    NAME: str = NotImplemented
    MANAGER_CLS: Type[BaseManager] = NotImplemented

    def create_environment(self, path: Path) -> Environment:
        """Create an empty python environment."""
        raise NotImplementedError

    def command(self, environment: Optional[Environment] = None) -> Tuple[str, ...]:
        """Manager command targeting the environment (current environment by default)."""
        raise NotImplementedError

    def manager(self, environment: Optional[Environment] = None) -> BaseManager:
        return self.MANAGER_CLS(*self.command(environment))

    def cli_command(self, environment: Optional[Environment] = None) -> str:
        """Value for the `--package-manager-command` CLI argument."""
        return " ".join(self.command(environment))


class PipCase(ManagerCase):
    NAME = "pip"
    MANAGER_CLS = PipManager

    def create_environment(self, path: Path) -> Environment:
        subprocess.check_call(  # noqa: S603 - Trusted test command;
            [sys.executable, "-m", "venv", str(path)]
        )
        return Environment(path)

    def command(self, environment: Optional[Environment] = None) -> Tuple[str, ...]:
        if environment is None:
            return tuple()
        return (environment.python, "-m", "pip")


class UvCase(ManagerCase):
    NAME = "uv"
    MANAGER_CLS = UvManager

    def create_environment(self, path: Path) -> Environment:
        subprocess.check_call(  # noqa: S603 - Trusted test command;
            ["uv", "venv", "--python", sys.executable, str(path)]  # noqa: S607
        )
        return Environment(path)

    def command(self, environment: Optional[Environment] = None) -> Tuple[str, ...]:
        if environment is None:
            return tuple()
        return ("uv", "--python", environment.python)


MANAGER_CASES: List[ManagerCase] = [PipCase(), UvCase()]

FREEZE_MANAGER_CASES: List[ManagerCase] = [
    case for case in MANAGER_CASES if issubclass(case.MANAGER_CLS, FreezeManager)
]


def _parametrize(cases: List[ManagerCase]):
    return pytest.mark.parametrize(
        "manager_case", cases, ids=[case.NAME for case in cases], indirect=True
    )


parametrize_managers = _parametrize(MANAGER_CASES)
"""Repeat the tests of a module for all package managers."""

parametrize_freeze_managers = _parametrize(FREEZE_MANAGER_CASES)
"""Repeat the tests of a module for all package managers that use the
`pip freeze` requirements format."""
