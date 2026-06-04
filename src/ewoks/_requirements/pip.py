import importlib.metadata
import logging
import sys
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional

from .utils import pip_freeze
from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements

logger = logging.getLogger(__name__)


class PipManagerInfo(BaseManagerInfo):
    name: Literal["pip"] = "pip"
    freeze: List[str]


class PipRequirements(BaseRequirements):
    manager: PipManagerInfo

    def __info__(self) -> str:
        freeze = "\n  ".join(self.manager.freeze)
        return f"{super().__info__()}\nRequirements:\n  {freeze}"


class PipManager(BaseManager):
    NAME = "pip"
    PRIORITY = 0
    REQUIREMENTS_MODEL = PipRequirements

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

    def _gather_requirements(self) -> Dict[str, Any]:
        freeze_output = self._check_output("freeze").strip().splitlines()

        return {"freeze": freeze_output}

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
