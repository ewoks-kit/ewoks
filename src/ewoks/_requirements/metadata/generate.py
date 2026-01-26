from ..models import get_model
from ..models.base import BaseRequirements
from .current import current_metadata


def generate_requirements(
    manager_name: str, manager_version: str, **kwargs
) -> BaseRequirements:
    model_cls = get_model(manager_name)
    manager = dict(name=manager_name, version=manager_version, **kwargs)
    return model_cls(manager=manager, **current_metadata())
