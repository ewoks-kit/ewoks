import importlib.metadata
import json
import os
import sys
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional

from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements


class PipenvManagerInfo(BaseManagerInfo):
    name: Literal["pipenv"] = "pipenv"
    requirements: List[str]


class PipenvRequirements(BaseRequirements):
    manager: PipenvManagerInfo

    def __info__(self) -> str:
        requirements = "\n  ".join(self.manager.requirements)
        return f"{super().__info__()}\nRequirements:\n  {requirements}"


class PipenvManager(BaseManager):
    NAME = "pipenv"
    PRIORITY = 3
    REQUIREMENTS_MODEL = PipenvRequirements

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

    def _gather_requirements(self) -> Dict[str, Any]:
        output = self._check_output("lock", "--requirements")
        requirements = output.strip().splitlines()

        return {"requirements": requirements}

    def _install_native_requirements(self, requirements: PipenvRequirements) -> bool:
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

    def _install_base_requirements(self, requirements: BaseRequirements) -> bool:
        raise NotImplementedError(f"{self.NAME} installation of python distributions")
