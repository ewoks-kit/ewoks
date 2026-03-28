from typing import List
from typing import Union

from ..models import get_model
from ..models.base import BaseRequirements
from .gather.pip_freeze import pip_freeze_requirements


def parse_requirements(requirements: Union[dict, List[str]]) -> BaseRequirements:
    if isinstance(requirements, list):
        # Legacy 'pip freeze' list
        requirements = pip_freeze_requirements(requirements)

    if not isinstance(requirements, dict):
        raise TypeError(
            f"Graph requirements must be a list or dictionary (type: {type(requirements)})"
        )

    manager = requirements.get("manager", dict()).get("name")
    return get_model(manager)(**requirements)
