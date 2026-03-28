from ..metadata.gather import gather_requirements
from ..models.uv import UvRequirements
from .utils.base import BaseManager


class UvManager(BaseManager):
    NAME = "uv"

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
