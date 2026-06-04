import importlib.metadata
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


class PoetryManagerInfo(BaseManagerInfo):
    name: Literal["poetry"] = "pip"
    requirements: List[str]


class PoetryRequirements(BaseRequirements):
    manager: PoetryManagerInfo


class PoetryManager(BaseManager):
    NAME = "poetry"
    PRIORITY = 2
    REQUIREMENTS_MODEL = PoetryRequirements

    def __init__(self, *command: str) -> None:
        if not command:
            command = sys.executable, "-m", "poetry"
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            return importlib.metadata.version("poetry")
        except importlib.metadata.PackageNotFoundError:
            return None

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return "POETRY_ACTIVE" in os.environ

    def _gather_requirements(self) -> Dict[str, Any]:
        output = self._check_output("export", "--without-hashes")
        requirements = output.strip().splitlines()

        return {"requirements": requirements}

    def _install_requirements(self, requirements: PoetryRequirements) -> None:
        text = "\n".join(requirements.requirements)
        with self._temporary_file(text, ".txt") as tmp_path:
            self._check_call("add", "--lock", "--file", tmp_path)
