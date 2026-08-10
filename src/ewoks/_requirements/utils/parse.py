from typing import List
from typing import Union

from ._supported import get_supported_managers
from .base_manager import BaseRequirements
from .metadata.from_requirements_txt import requirements_txt_metadata


def parse_requirements(requirements: Union[dict, List[str]]) -> BaseRequirements:
    if isinstance(requirements, list):
        # Legacy 'pip freeze' list
        requirements = requirements_txt_metadata(requirements)

    if not isinstance(requirements, dict):
        raise TypeError(
            f"Graph requirements must be a list or dictionary (type: {type(requirements)})"
        )

    manager_name = requirements.get("manager", dict()).get("name")

    managers = get_supported_managers()
    if manager_name not in managers:
        raise ValueError(f"{manager_name!r} is not a valid package manager")

    return managers[manager_name].REQUIREMENTS_MODEL(**requirements)
