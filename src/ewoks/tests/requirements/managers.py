"""Package manager specific knowledge needed by the package manager tests.

Add a `ManagerCase` to `MANAGER_CASES` to include a package manager in the
tests that apply to all package managers. The tests use the `manager_case`,
`manager` and `environment` fixtures (see `conftest.py`).
"""

from typing import Dict
from typing import List
from typing import Sequence
from typing import Tuple
from typing import Type

from ..._requirements.pip_venv import PipVenvManager
from ..._requirements.utils.base_manager import BaseManager
from ..._requirements.utils.metadata import models
from ..._requirements.utils.requirements_txt import REQUIREMENTS_FILENAME
from ..._requirements.uv import UvManager


class ManagerCase:
    NAME: str = NotImplemented

    MANAGER_CLS: Type[BaseManager] = NotImplemented

    INSTALLER: str = NotImplemented
    """`INSTALLER` metadata of a distribution installed by the package manager."""

    SLOW: bool = False
    """Creating an environment takes tens of seconds."""

    def command(self) -> Tuple[str, ...]:
        """Command that invokes the package manager (the default when empty)."""
        return tuple()

    def manager(self) -> BaseManager:
        return self.MANAGER_CLS(*self.command())

    def cli_command(self) -> str:
        """Value for the `--package-manager-command` CLI argument."""
        return " ".join(self.command())

    def native_files(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        """Files the package manager generates to reproduce an environment with
        these distributions. Empty when they cannot be generated.
        """
        raise NotImplementedError


class PipVenvCase(ManagerCase):
    NAME = "pip-venv"
    MANAGER_CLS = PipVenvManager
    INSTALLER = "pip"

    def native_files(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        requirements = "\n".join(
            f"{dist.name}=={dist.version}" for dist in distributions
        )
        return {REQUIREMENTS_FILENAME: requirements}


class UvCase(ManagerCase):
    NAME = "uv"
    MANAGER_CLS = UvManager
    INSTALLER = "uv"

    def native_files(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        # Resolving a lock file requires the package index
        try:
            return UvManager()._files_from_distributions(distributions, python_version)
        except RuntimeError:
            return dict()


MANAGER_CASES: List[ManagerCase] = [
    PipVenvCase(),
    UvCase(),
]

FAST_MANAGER_CASES: List[ManagerCase] = [
    case for case in MANAGER_CASES if not case.SLOW
]
