from ...models import get_model
from ...models.base import BaseRequirements
from .current import current_requirements


def gather_requirements(
    manager_name: str, manager_version: str, **parameters
) -> BaseRequirements:
    """
    :raises ValueError: unknown package manager
    :raises ValidationError: wrong parameters
    """
    model_cls = get_model(manager_name)
    manager = dict(name=manager_name, version=manager_version, **parameters)
    return model_cls(manager=manager, **current_requirements())
