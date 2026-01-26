from typing import List
from typing import Union

from ..models import get_model
from ..models.base import BaseRequirements


def parse_requirements(requirements: Union[dict, List[str]]) -> BaseRequirements:
    if isinstance(requirements, list):
        requirements = _generate_requirements_from_pip_freeze(requirements)

    if not isinstance(requirements, dict):
        raise TypeError(
            f"Graph requirements must be a list or dictionary (type: {type(requirements)})"
        )

    schema_version = requirements.get("schema_version")
    if not schema_version:
        raise ValueError("Invalid requirements: 'schema_version' is missing")

    manager = requirements.get("manager", dict()).get("name")
    return get_model(manager)(**requirements)


def _generate_requirements_from_pip_freeze(requirements: List[str]) -> dict:
    manager = dict(manager="pip", version="unknown")
    system = dict()
    python = dict()

    return dict(
        manager=manager, system=system, python=python, requirements=requirements
    )
