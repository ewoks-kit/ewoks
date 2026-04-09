import logging

import yaml

from ..metadata.gather import gather_requirements
from ..models.conda import CondaRequirements
from .utils.base import BaseManager

logger = logging.getLogger(__name__)


class CondaManager(BaseManager):
    NAME = "conda"

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
