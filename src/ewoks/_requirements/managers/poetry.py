from ..metadata.gather import gather_requirements
from ..models.poetry import PoetryRequirements
from .utils.base import BaseManager


class PoetryManager(BaseManager):
    NAME = "poetry"

    def _gather_requirements(self, manager_version: str) -> PoetryRequirements:
        output = self._check_output("export", "--without-hashes")
        requirements = output.strip().splitlines()

        return gather_requirements(
            manager_name=self.NAME,
            manager_version=manager_version,
            requirements=requirements,
        )

    def _install_requirements(self, requirements: PoetryRequirements) -> None:
        text = "\n".join(requirements.requirements)
        with self._temporary_file(text, ".txt") as tmp_path:
            self._check_call("add", "--lock", "--file", tmp_path)
