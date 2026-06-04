from typing import Optional

from ..metadata.gather import gather_requirements
from ..models.uv import UvRequirements
from .utils.base import BaseManager


class UvManager(BaseManager):
    NAME = "uv"
    PRIORITY = 1

    def __init__(self, *command: str) -> None:
        if not command:
            command = ("uv",)
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            output = self._check_output("--version")
            return output.strip().split(" ")[-1]
        except RuntimeError:
            return None

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        pass

    def _gather_requirements(self, manager_version: str) -> UvRequirements:
        output = self._check_output("pip", "freeze")
        requirements = output.strip().splitlines()

        return gather_requirements(
            manager_name=self.NAME,
            manager_version=manager_version,
            requirements=requirements,
        )

    def _install_requirements(self, requirements: UvRequirements) -> None:
        text = "\n".join(requirements.requirements)
        with self._temporary_file(text, ".txt") as tmp_path:
            self._check_call("add", "-r", tmp_path)
