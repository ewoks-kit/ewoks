import logging
import os
import sys
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional
from typing import Tuple

import yaml

from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements

logger = logging.getLogger(__name__)


class CondaManagerInfo(BaseManagerInfo):
    name: Literal["conda"] = "conda"


class CondaRequirements(BaseRequirements):
    manager: CondaManagerInfo
    environment: dict


class CondaManager(BaseManager):
    NAME = "conda"
    PRIORITY = 4
    REQUIREMENTS_MODEL = CondaRequirements

    def __init__(self, *command: str) -> None:
        if not command:
            command = self._get_conda_command()
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            output = self._check_output("--version")
        except RuntimeError:
            return None
        return output.strip().split(" ")[-1]

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return "CONDA_PREFIX" in os.environ or os.path.exists(
            os.path.join(sys.prefix, "conda-meta")
        )

    def _gather_requirements(self) -> Dict[str, Any]:
        output = self._check_output("env", "export")
        environment = yaml.safe_load(output)
        environment.pop("name", None)
        environment.pop("prefix", None)

        return {"environment": environment}

    def _install_native_requirements(self, requirements: CondaRequirements) -> bool:
        text = yaml.safe_dump(requirements.environment)
        with self._temporary_file(text, ".yml") as tmp_path:
            self._check_call("env", "update", "-f", tmp_path)
        return True

    def _install_base_requirements(self, requirements: BaseRequirements) -> bool:
        raise NotImplementedError(f"{self.NAME} installation of python distributions")

    def _get_conda_command(self) -> Tuple[str, ...]:
        try:
            _ = self._check_output_raw("mamba", "--version")
            return ("mamba",)
        except Exception:  # noqa S110
            pass
        try:
            _ = self._check_output_raw("micromamba", "--version")
            return ("micromamba",)
        except Exception:  # noqa S110
            pass
        return ("conda",)
