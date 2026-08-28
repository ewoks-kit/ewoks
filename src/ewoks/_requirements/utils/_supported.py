from functools import lru_cache
from typing import Dict
from typing import Type

from ..pip_venv import PipVenvManager
from ..pixi import PixiManager
from ..uv import UvManager
from .base_manager import BaseManager


@lru_cache(1)
def get_supported_managers() -> Dict[str, Type[BaseManager]]:
    managers = [
        PipVenvManager,
        UvManager,
        PixiManager,
    ]
    return {manager_cls.NAME: manager_cls for manager_cls in managers}
