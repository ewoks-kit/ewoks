import os
import re
import sys
from typing import List
from typing import Literal
from typing import Optional
from typing import Sequence
from typing import Tuple

from .utils.freeze_manager import FreezeManager
from .utils.freeze_manager import FreezeManagerInfo
from .utils.freeze_manager import FreezeRequirements


class UvManagerInfo(FreezeManagerInfo):
    name: Literal["uv"] = "uv"


class UvRequirements(FreezeRequirements):
    manager: UvManagerInfo


class UvManager(FreezeManager):
    """Uses the `uv pip` interface which, unlike `uv add` or `uv sync`, does not
    require a uv project.

    The command may end with options for `uv pip` to select the target
    environment. For example `UvManager("uv", "--python", "/path/to/python")`.
    The current python environment is the target when no options are provided.
    """

    NAME = "uv"
    PRIORITY = 1
    REQUIREMENTS_MODEL = UvRequirements
    COMMAND_EXAMPLE = "uv --python /path/to/python"

    def __init__(self, *command: str) -> None:
        if not command:
            command = ("uv",)
        super().__init__(*command)
        self._executable, self._options = _split_options(command)
        if not self._options:
            self._options = ("--python", sys.executable)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            output = self._check_output_raw(*self._executable, "--version")
        except RuntimeError:
            return None
        # For example "uv 0.12.1 (x86_64-unknown-linux-gnu)"
        match = re.search(r"(\d+\.\d+(?:\.\d+)*)", output)
        if not match:
            return None
        return match.group(1)

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return "UV" in os.environ or _created_by_uv(sys.prefix)

    def _freeze(self) -> str:
        return self._check_output_raw(
            *self._executable, "pip", "freeze", *self._options
        )

    def _install(self, arguments: List[str]) -> None:
        self._check_call_raw(
            *self._executable,
            "pip",
            "install",
            "--no-cache",
            *arguments,
            *self._options,
        )


def _split_options(command: Sequence[str]) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """Split a uv command in the executable part and the `uv pip` options."""
    for index, argument in enumerate(command):
        if argument.startswith("-"):
            return tuple(command[:index]), tuple(command[index:])
    return tuple(command), tuple()


def _created_by_uv(prefix: str) -> bool:
    """Environment is a virtual environment created by uv."""
    filename = os.path.join(prefix, "pyvenv.cfg")
    try:
        with open(filename, "r", encoding="utf-8") as fh:
            return any(line.split("=")[0].strip() == "uv" for line in fh)
    except OSError:
        return False
