import json

from ..metadata.generate import generate_requirements
from ..models.pipenv import PipenvRequirements
from .utils.base import BaseManager


class PipenvManager(BaseManager):

    NAME = "pipenv"

    def _generate_requirements(self, manager_version: str) -> PipenvRequirements:
        output = self._check_output("lock", "--requirements")
        requirements = output.strip().splitlines()

        return generate_requirements(
            manager_name=self.NAME,
            manager_version=manager_version,
            requirements=requirements,
        )

    def _install_requirements(self, requirements: PipenvRequirements) -> None:
        lock_data = {
            "_meta": {"hash": {"sha256": "dummy"}},  # minimal metadata
            "default": {
                pkg.split("==")[0]: {"version": pkg.split("==")[1]}
                for pkg in requirements.requirements
            },
            "develop": {
                pkg.split("==")[0]: {"version": pkg.split("==")[1]}
                for pkg in getattr(requirements, "dev_requirements", [])
            },
        }
        text = json.dumps(lock_data, indent=2)

        with self._temporary_file(text, ".lock") as tmp_path:
            self._check_call("sync", "--ignore-pipfile", "-f", tmp_path)
