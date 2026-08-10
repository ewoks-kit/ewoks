from functools import lru_cache
from typing import Dict
from typing import Type

from ..pip_venv import PipVenvManager
from .base_manager import BaseManager


@lru_cache(1)
def get_supported_managers() -> Dict[str, Type[BaseManager]]:
    managers = [
        PipVenvManager,
    ]
    return {manager_cls.NAME: manager_cls for manager_cls in managers}
