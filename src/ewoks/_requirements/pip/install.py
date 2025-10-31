import logging
import subprocess
from typing import Sequence

from .sanitize import sanitize_requirements

logger = logging.getLogger(__name__)


def pip_install(requirements: Sequence[str], python_path: str) -> int:
    requirements, warnings = sanitize_requirements(requirements)
    for warning in warnings:
        logger.warning(warning)
    # https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program
    return subprocess.check_call([python_path, "-m", "pip", "install", *requirements])
