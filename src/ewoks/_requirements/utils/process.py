import logging
import os
import subprocess
from pathlib import Path
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import Union

logger = logging.getLogger(__name__)


def check_output(
    *args: Union[str, Path], extra_env: Optional[Mapping[str, Optional[str]]] = None
) -> str:
    """`extra_env` adds environment variables to the current ones, or removes them
    when their value is `None`.

    :raises RuntimeError: command failed
    """
    logger.debug("Capture output of %s", args)
    try:
        return subprocess.check_output(  # noqa: S603 - Internal manager call
            args, text=True, env=_environment(extra_env)
        )
    except Exception as ex:
        raise RuntimeError(f"Command failed: {args}") from ex


def check_call(
    *args: Union[str, Path], extra_env: Optional[Mapping[str, Optional[str]]] = None
) -> None:
    """`extra_env` adds environment variables to the current ones, or removes them
    when their value is `None`.

    :raises RuntimeError: command failed
    """
    logger.debug("Execute %s", args)
    try:
        subprocess.check_call(  # noqa: S603 - Internal manager call
            args, env=_environment(extra_env)
        )
    except Exception as ex:
        raise RuntimeError(f"Command failed: {args}") from ex


def _environment(
    extra_env: Optional[Mapping[str, Optional[str]]],
) -> Optional[Dict[str, str]]:
    if not extra_env:
        return None
    environment = {**os.environ, **extra_env}
    return {name: value for name, value in environment.items() if value is not None}
