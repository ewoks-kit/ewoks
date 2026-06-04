from functools import lru_cache
from typing import Dict

from ..pip import PipManager
from .base import BaseManager

# from ..conda import CondaManager
# from ..pipenv import PipenvManager
# from ..pixi import PixiManager
# from ..poetry import PoetryManager
# from ..uv import UvManager


@lru_cache(maxsize=None)
def get_supported_managers(*command: str) -> Dict[str, BaseManager]:
    managers = [
        PipManager(*command),  # UvManager(*command),
        # PoetryManager(*command),
        # PipenvManager(*command),
        # CondaManager(*command),
        # PixiManager(*command),
    ]
    return {manager.NAME: manager for manager in managers}
