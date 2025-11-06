import logging

from ..metadata.generate import generate_requirements
from ..metadata.pip_freeze import sanitize_pip_freeze
from ..models.pip import PipRequirements
from .utils.base import BaseManager

logger = logging.getLogger(__name__)


class PipManager(BaseManager):

    NAME = "pip"

    def _generate_requirements(self, manager_version: str) -> PipRequirements:
        freeze_output = self._check_output("freeze")
        requirements = freeze_output.strip().splitlines()

        return generate_requirements(
            manager_name=self.NAME,
            manager_version=manager_version,
            requirements=requirements,
        )

    def _install_requirements(self, requirements: PipRequirements) -> None:
        sanitized, warnings = sanitize_pip_freeze(requirements.requirements)
        for warning in warnings:
            logger.warning(warning)

        self._check_call("install", "--no-cache-dir", *sanitized)
