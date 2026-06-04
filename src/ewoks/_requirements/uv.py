from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional

from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements


class UvManagerInfo(BaseManagerInfo):
    name: Literal["uv"] = "uv"
    requirements: List[str]


class UvRequirements(BaseRequirements):
    manager: UvManagerInfo

    def __info__(self) -> str:
        requirements = "\n  ".join(self.manager.requirements)
        return f"{super().__info__()}\nRequirements:\n  {requirements}"


class UvManager(BaseManager):
    NAME = "uv"
    PRIORITY = 1
    REQUIREMENTS_MODEL = UvRequirements

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

    def _gather_requirements(self) -> Dict[str, Any]:
        output = self._check_output("pip", "freeze")
        requirements = output.strip().splitlines()

        return {"requirements": requirements}

    def _install_requirements(self, requirements: UvRequirements) -> None:
        text = "\n".join(requirements.requirements)
        with self._temporary_file(text, ".txt") as tmp_path:
            self._check_call("add", "-r", tmp_path)
