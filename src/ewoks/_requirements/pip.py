import importlib.metadata
import sys
from typing import List
from typing import Literal
from typing import Optional

from .utils.freeze_manager import FreezeManager
from .utils.freeze_manager import FreezeManagerInfo
from .utils.freeze_manager import FreezeRequirements


class PipManagerInfo(FreezeManagerInfo):
    name: Literal["pip"] = "pip"


class PipRequirements(FreezeRequirements):
    manager: PipManagerInfo


class PipManager(FreezeManager):
    """Uses the `pip` module of a python interpreter.

    The command selects the target environment. For example
    `PipManager("/path/to/python", "-m", "pip")`. The current python
    environment is the target when no command is provided.
    """

    NAME = "pip"
    PRIORITY = 0
    REQUIREMENTS_MODEL = PipRequirements
    COMMAND_EXAMPLE = "python -m pip"

    def __init__(self, *command: str) -> None:
        if not command:
            command = sys.executable, "-m", "pip"
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            return importlib.metadata.version("pip")
        except importlib.metadata.PackageNotFoundError:
            return None

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return False

    def _freeze(self) -> str:
        return self._check_output("freeze")

    def _install(self, arguments: List[str]) -> None:
        self._check_call("install", "--no-cache-dir", *arguments)
