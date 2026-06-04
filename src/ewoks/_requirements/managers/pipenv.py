import importlib.metadata
import json
import os
import sys
from typing import Optional

from ..metadata.gather import gather_requirements
from ..models.pipenv import PipenvRequirements
from .utils.base import BaseManager


class PipenvManager(BaseManager):
    NAME = "pipenv"
    PRIORITY = 3

    def __init__(self, *command: str) -> None:
        if not command:
            command = sys.executable, "-m", "pipenv"
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            return importlib.metadata.version("pipenv")
        except importlib.metadata.PackageNotFoundError:
            return None

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return "PIPENV_ACTIVE" in os.environ

    def _gather_requirements(self, manager_version: str) -> PipenvRequirements:
        output = self._check_output("lock", "--requirements")
        requirements = output.strip().splitlines()

        return gather_requirements(
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
