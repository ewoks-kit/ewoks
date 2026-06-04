import logging
import os
import subprocess
import tempfile
from abc import abstractmethod
from contextlib import contextmanager
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional

from .metadata import metadata_models
from .metadata.from_python import current_requirements

logger = logging.getLogger(__name__)


class BaseManagerInfo(metadata_models.BaseModel):
    name: str
    version: str


class BaseRequirements(metadata_models.BaseModel):
    system: metadata_models.SystemInfo
    python: metadata_models.PythonInfo
    distributions: List[metadata_models.Distribution]
    manager: BaseManagerInfo

    def __info__(self) -> str:
        return (
            f"Manager: {self.manager.name} ({self.manager.version}) "
            f"python={self.python.version}) "
            f"distributions={len(self.distributions)}"
        )


class BaseManager:
    """Defines the interface all package managers must implement.

    If `MyManager` is an implementation of this interface then
    Ewoks workflow requirements can be obtained like this:

    .. code-block:: python

        manager = MyManager()
        requirements = manager.gather_requirements()

    Ewoks workflow requirements can be installed like this:

    .. code-block:: python

        manager = MyManager()
        manager.install_requirements(requirements)
    """

    NAME = NotImplemented
    PRIORITY = NotImplemented
    REQUIREMENTS_MODEL = NotImplemented

    def __init__(self, *command: str) -> None:
        if not command:
            raise ValueError(f"{type(self).__name__} needs an associated shell command")
        self._cmd_args = command

    def gather_requirements(self) -> Optional[BaseRequirements]:
        """Return requirements generated from the current python environment."""
        manager_version = self.version()
        if manager_version is None:
            raise RuntimeError(f"{self.NAME!r} is not installed")

        try:
            parameters = self._gather_requirements()
        except Exception as ex:
            logger.error(
                "%s: failed to generate requirements (%s)", type(self).__name__, ex
            )
            return None

        manager = dict(name=self.NAME, version=manager_version, **parameters)
        return self.REQUIREMENTS_MODEL(manager=manager, **current_requirements())

    @abstractmethod
    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Manager is explicitly active."""
        pass

    def install_requirements(self, requirements: BaseRequirements) -> None:
        """Install requirements into the current python environment."""
        try:
            return self._install_requirements(requirements)
        except Exception as ex:
            logger.error(
                "%s: failed to install requirements (%s)", type(self).__name__, ex
            )
            raise

    @abstractmethod
    def _gather_requirements(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _install_requirements(self, requirements: BaseRequirements) -> None:
        pass

    def _check_output(self, *args: str) -> str:
        return self._check_output_raw(*[*self._cmd_args, *args])

    def _check_call(self, *args: str) -> int:
        return self._check_call_raw(*[*self._cmd_args, *args])

    @staticmethod
    def _check_output_raw(*args: str) -> str:
        try:
            return subprocess.check_output(args, text=True)
        except Exception as ex:
            raise RuntimeError(f"Command failed: {args}") from ex

    @staticmethod
    def _check_call_raw(*args: str) -> int:
        try:
            return subprocess.check_call(args)
        except Exception as ex:
            raise RuntimeError(f"Command failed: {args}") from ex

    @contextmanager
    def _temporary_file(self, text: str, suffix: str) -> Generator[str, None, None]:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False) as tmp:
                tmp.write(text)
                tmp_path = tmp.name

            yield tmp_path

        finally:
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except OSError:
                    logger.debug("Could not delete temporary file: %s", tmp_path)
