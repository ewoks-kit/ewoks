import logging
import os
import sys
from typing import Optional
from typing import Tuple

import yaml

from ..metadata.gather import gather_requirements
from ..models.conda import CondaRequirements
from .utils.base import BaseManager

logger = logging.getLogger(__name__)


class CondaManager(BaseManager):
    NAME = "conda"
    PRIORITY = 4

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

    def _gather_requirements(self, manager_version: str) -> CondaRequirements:
        output = self._check_output("env", "export")
        environment = yaml.safe_load(output)
        environment.pop("name", None)
        environment.pop("prefix", None)

        return gather_requirements(
            manager_name="conda",
            manager_version=manager_version,
            environment=environment,
        )

    def install_requirements(self, requirements: CondaRequirements) -> None:
        text = yaml.safe_dump(requirements.environment)
        with self._temporary_file(text, ".yml") as tmp_path:
            self._check_call("env", "update", "-f", tmp_path)

    def _get_conda_command(self) -> Tuple[str, ...]:
        try:
            _ = self._check_output_raw("mamba", "--version")
            return ("mamba",)
        except Exception:
            pass
        try:
            _ = self._check_output_raw("micromamba", "--version")
            return ("micromamba",)
        except Exception:
            pass
        return ("conda",)
