import os
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional

from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements


class PixiManagerInfo(BaseManagerInfo):
    name: Literal["pixi"] = "pixi"
    lockfile: str


class PixiRequirements(BaseRequirements):
    manager: PixiManagerInfo


class PixiManager(BaseManager):
    NAME = "pixi"
    PRIORITY = 5
    REQUIREMENTS_MODEL = PixiRequirements
    COMMAND_EXAMPLE = "pixi"

    def __init__(self, *command: str) -> None:
        if not command:
            command = ("pixi",)
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            output = self._check_output("--version", text=True)
            return output.strip().split(" ")[-1]
        except Exception:
            return None

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return "PIXI_PROJECT_ROOT" in os.environ

    def _gather_requirements(self) -> Dict[str, Any]:
        if os.path.exists("pixi.lock"):
            with open("pixi.lock", "r", encoding="utf-8") as f:
                lock_content = f.read()
        elif os.path.exists("pixi.toml"):
            with open("pixi.toml", "r", encoding="utf-8") as f:
                lock_content = f.read()
        else:
            raise RuntimeError("No pixi.lock or pixi.toml file found")

        return {"lockfile": lock_content}

    def _install_requirements(self, requirements: PixiRequirements) -> bool:
        with self._temporary_file(requirements.lockfile, ".lock") as tmp_path:
            self._check_call("install", cwd=os.path.dirname(tmp_path))

        return True

    def _install_base_requirements(self, requirements: BaseRequirements) -> bool:
        raise NotImplementedError(f"{self.NAME} installation of python distributions")
