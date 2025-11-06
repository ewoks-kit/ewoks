import logging
from typing import Optional
from typing import Tuple

from ..conda import CondaManager
from ..fallback import FallbackManager
from ..pip import PipManager
from ..pipenv import PipenvManager
from ..pixi import PixiManager
from ..poetry import PoetryManager
from ..uv import UvManager
from .base import BaseManager
from .versions import manager_versions

logger = logging.getLogger(__name__)


def get_manager(
    manager_name: Optional[str] = None, command: Tuple[str] = tuple()
) -> BaseManager:
    if manager_name is None:
        cls = _detect_manager()
    else:
        if manager_name not in _MANAGERS:
            raise ValueError(f"{manager_name!r} is not a valid package manager")
        cls = _MANAGERS[manager_name]
    return cls(*command)


_MANAGERS = {
    "pip": PipManager,
    "poetry": PoetryManager,
    "pipenv": PipenvManager,
    "uv": UvManager,
    "conda": CondaManager,
    "pixi": PixiManager,
}

_PRIORITY = {
    "pip": 0,
    # "pipenv": -1,
    # "uv": -1,
    # "poetry": -1,
    "conda": 1,
    "pixi": 2,
}


def _detect_manager() -> BaseManager:
    manager_names = {
        k: _PRIORITY[k] for k, v in manager_versions().items() if v and k in _PRIORITY
    }
    if not manager_names:
        logger.debug("No managers available: use fallback")
        return FallbackManager
    manager_names = [
        k for k, _ in sorted(manager_names.items(), key=lambda tpl: tpl[1])
    ]
    manager_name = manager_names[-1]
    logger.debug("Selected %r from available %s", manager_name, manager_names)
    return _MANAGERS[manager_name]
