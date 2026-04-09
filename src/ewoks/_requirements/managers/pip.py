import logging
from typing import List

from ..metadata import pip_freeze
from ..metadata.gather import gather_requirements
from ..models.pip import PipRequirements
from .utils.base import BaseManager

logger = logging.getLogger(__name__)


class PipManager(BaseManager):
    NAME = "pip"

    def _gather_requirements(self, manager_version: str) -> PipRequirements:
        freeze_output = self._check_output("freeze").strip().splitlines()
        return gather_requirements(
            manager_name=self.NAME,
            manager_version=manager_version,
            freeze=freeze_output,
        )

    def _install_requirements(self, requirements: PipRequirements) -> None:
        freeze = requirements.manager.freeze

        if freeze:
            arguments = self._arguments(freeze)
            try:
                self._check_call("install", "--no-cache-dir", *arguments)
                return
            except Exception:
                if not requirements.distributions:
                    raise

        freeze = self.freeze_distributions(requirements)
        if freeze:
            arguments = self._arguments(freeze)
            self._check_call("install", "--no-cache-dir", *arguments)
            return

        raise ValueError("No distibutions provided to install")

    def freeze_distributions(self, requirements: PipRequirements) -> List[str]:
        freeze = []
        for dist in requirements.distributions:
            lines, warnings = pip_freeze.freeze_distribution(dist)
            for warning in warnings:
                logger.warning(warning)
            freeze.extend(lines)
        return freeze

    def _arguments(self, freeze: List[str]) -> List[str]:
        arguments, warnings = pip_freeze.sanitize_freeze(freeze)
        for warning in warnings:
            logger.warning(warning)
        return arguments
