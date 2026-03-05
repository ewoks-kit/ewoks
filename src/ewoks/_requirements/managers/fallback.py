import logging
import sys
from typing import Generator

from ..metadata.generate import generate_requirements
from ..metadata.native import distribution_to_pip_requirement
from ..metadata.native import distributions
from ..models.pip import PipRequirements
from .utils.base import BaseManager

logger = logging.getLogger(__name__)


class FallbackManager(BaseManager):
    """Like PipManager but does not expect 'pip' to be available."""

    NAME = "pip"

    def _generate_requirements(self, manager_version: str) -> PipRequirements:
        """Does not use 'pip'."""
        requirements = list(_generate_requirements())

        return generate_requirements(
            manager_name=self.NAME,
            manager_version=manager_version,
            requirements=requirements,
        )

    def _install_requirements(self, requirements: PipRequirements) -> None:
        """Installs pip when needed."""
        self._check_call(sys.executable, "-m", "ensurepip", raw=True)
        self._check_call("install", "--no-cache-dir", *requirements.requirements)


def _generate_requirements() -> Generator[str, None, None]:
    """Generate pip requirements without pip."""
    for dist in distributions():
        for line in distribution_to_pip_requirement(dist):
            yield line
