from typing import Type

from ..models.base import BaseRequirements
from ..models.conda import CondaRequirements
from ..models.pip import PipRequirements
from ..models.pipenv import PipenvRequirements
from ..models.pixi import PixiRequirements
from ..models.poetry import PoetryRequirements
from ..models.uv import UvRequirements

_REQUIREMENT_MODELS = {
    "pip": PipRequirements,
    "poetry": PoetryRequirements,
    "pipenv": PipenvRequirements,
    "uv": UvRequirements,
    "conda": CondaRequirements,
    "pixi": PixiRequirements,
}


def get_model(manager_name: str) -> Type[BaseRequirements]:
    if manager_name not in _REQUIREMENT_MODELS:
        raise ValueError(f"{manager_name!r} is not a valid package manager")
    return _REQUIREMENT_MODELS[manager_name]
