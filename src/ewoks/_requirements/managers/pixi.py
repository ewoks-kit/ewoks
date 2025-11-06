import os

from ..metadata.generate import generate_requirements
from ..models.pixi import PixiRequirements
from .utils.base import BaseManager


class PixiManager(BaseManager):

    NAME = "pixi"

    def _generate_requirements(self, manager_version: str) -> PixiRequirements:
        if os.path.exists("pixi.lock"):
            with open("pixi.lock", "r", encoding="utf-8") as f:
                lock_content = f.read()
        elif os.path.exists("pixi.toml"):
            with open("pixi.toml", "r", encoding="utf-8") as f:
                lock_content = f.read()
        else:
            raise RuntimeError("No pixi.lock or pixi.toml file found")

        return generate_requirements(
            manager_name=self.NAME,
            manager_version=manager_version,
            lockfile=lock_content,
        )

    def _install_requirements(self, requirements: PixiRequirements) -> None:
        with self._temporary_file(requirements.lockfile, ".lock") as tmp_path:
            self._check_call("install", cwd=os.path.dirname(tmp_path))
