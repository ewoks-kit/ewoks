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

from ..._requirements.conda import CondaManager
from ..._requirements.pip_venv import PipVenvManager
from ..._requirements.pixi import PixiManager
from ..._requirements.poetry import PoetryManager
from ..._requirements.utils import conda_channel
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

    CHANNEL_PYTHON: bool = False
    """Python comes from a conda channel, which decides the patch version."""

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


class PoetryCase(ManagerCase):
    NAME = "poetry"
    MANAGER_CLS = PoetryManager
    INSTALLER = "Poetry 1.8.5"  # poetry adds its version

    def native_files(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        # Resolving a lock file requires the package index
        try:
            return PoetryManager()._files_from_distributions(
                distributions, python_version
            )
        except RuntimeError:
            return dict()


class CondaCase(ManagerCase):
    NAME = "conda"
    MANAGER_CLS = CondaManager
    INSTALLER = "conda"
    SLOW = True
    CHANNEL_PYTHON = True

    def native_files(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        pip_dependencies = "".join(
            f"    - {dist.name}=={dist.version}\n" for dist in distributions
        )
        return {
            "environment.yml": f"""channels:
  - conda-forge
dependencies:
  - python={conda_channel.python_specifier(python_version)}
  - pip
  - pip:
{pip_dependencies}"""
        }


class PixiCase(ManagerCase):
    NAME = "pixi"
    MANAGER_CLS = PixiManager
    INSTALLER = "uv-pixi"  # pixi installs PyPI distributions with its own uv
    SLOW = True
    CHANNEL_PYTHON = True

    def native_files(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        # Resolving a lock file requires the package index
        try:
            return PixiManager()._files_from_distributions(
                distributions, python_version
            )
        except RuntimeError:
            return dict()


MANAGER_CASES: List[ManagerCase] = [
    PipVenvCase(),
    UvCase(),
    PoetryCase(),
    CondaCase(),
    PixiCase(),
]

FAST_MANAGER_CASES: List[ManagerCase] = [
    case for case in MANAGER_CASES if not case.SLOW
]
