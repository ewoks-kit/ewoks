from functools import lru_cache
from typing import Dict
from typing import Type

from ..pip import PipManager
from ..uv import UvManager
from .base_manager import BaseManager

# from ..conda import CondaManager
# from ..pipenv import PipenvManager
# from ..pixi import PixiManager
# from ..poetry import PoetryManager


@lru_cache(1)
def get_supported_managers() -> Dict[str, Type[BaseManager]]:
    managers = [
        PipManager,
        UvManager,
        # PoetryManager,
        # PipenvManager,
        # CondaManager,
        # PixiManager,
    ]
    return {manager_cls.NAME: manager_cls for manager_cls in managers}
