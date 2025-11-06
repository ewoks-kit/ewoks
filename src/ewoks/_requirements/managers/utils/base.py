import logging
import os
import subprocess
import tempfile
from abc import abstractmethod
from contextlib import contextmanager
from typing import Generator
from typing import Optional

from ...models.base import BaseRequirements
from .commands import get_manager_command
from .versions import get_manager_version

logger = logging.getLogger(__name__)


class BaseManager:
    """Defines the interface all package managers must implement."""

    NAME = NotImplemented

    def __init__(self, *command: str) -> None:
        if not command:
            command = get_manager_command(self.NAME)
        self._cmd_args = command

    def generate_requirements(self) -> Optional[BaseRequirements]:
        """Return requirements generated from the current python environment."""
        try:
            manager_version = get_manager_version(self.NAME)
            return self._generate_requirements(manager_version)
        except Exception as ex:
            logger.error(
                "%s: failed to generate requirements (%s)", type(self).__name__, ex
            )
            return None

    def install_requirements(self, requirements: BaseRequirements) -> None:
        """Install requirements into the current python environment."""
        try:
            return self._install_requirements()
        except Exception as ex:
            logger.error(
                "%s: failed to install requirements (%s)", type(self).__name__, ex
            )
            raise

    @abstractmethod
    def _generate_requirements(self, manager_version: str) -> BaseRequirements:
        pass

    @abstractmethod
    def _install_requirements(self, requirements: BaseRequirements) -> None:
        pass

    def _check_output(self, *args) -> str:
        return subprocess.check_output([*self._cmd_args, *args], text=True)

    def _check_call(self, *args, raw: bool = False) -> int:
        if raw:
            return subprocess.check_call([*args])
        return subprocess.check_call([*self._cmd_args, *args])

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
