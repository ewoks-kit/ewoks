import logging
from collections import Counter
from functools import lru_cache
from typing import Dict
from typing import Optional
from typing import Tuple

from ._supported import get_supported_managers
from .base_manager import BaseManager
from .base_manager import BaseRequirements
from .metadata.from_python import current_requirements

logger = logging.getLogger(__name__)


def get_manager(
    manager_name: Optional[str] = None,
    manager_command: Tuple[str, ...] = tuple(),
) -> BaseManager:
    """Package manager that describes the current python environment.

    :raise ValueError: package manager not supported or not available
    :raise RuntimeError: no package manager available
    """
    if manager_name:
        return _select_manager(manager_name, manager_command)

    if manager_command:
        raise ValueError(
            f"Provide 'manager_name' associated to command {manager_command}"
        )

    manager = _detect_manager()

    if manager is None:
        raise RuntimeError("No known package manager installed or available")

    return manager


def get_installer(
    requirements: BaseRequirements,
    manager_name: Optional[str] = None,
    manager_command: Tuple[str, ...] = tuple(),
) -> BaseManager:
    """Package manager that installs requirements. The package manager that
    generated the requirements is used when available.

    :raise ValueError: package manager not supported or not available
    :raise RuntimeError: no package manager available
    """
    if manager_name:
        return _select_manager(manager_name, manager_command)

    if manager_command:
        raise ValueError(
            f"Provide 'manager_name' associated to command {manager_command}"
        )

    try:
        return _select_manager(requirements.manager.name, tuple())
    except ValueError:
        logger.debug(
            "Package manager %r that generated the requirements is not available",
            requirements.manager.name,
        )

    managers = _managers()
    scores = {name: (manager.PRIORITY,) for name, manager in managers.items()}
    manager = _first_available(managers, scores)
    if manager is None:
        raise RuntimeError("No known package manager installed or available")

    return manager


def get_in_place_installer() -> BaseManager:
    """Package manager that can install in the current python environment.

    :raise RuntimeError: no package manager available
    """
    managers = {
        name: manager
        for name, manager in _managers().items()
        if manager.CAN_INSTALL_IN_PLACE
    }
    scores = {name: (manager.PRIORITY,) for name, manager in managers.items()}
    manager = _first_available(managers, scores)
    if manager is None:
        raise RuntimeError(
            "No package manager available that can install in the current python "
            "environment"
        )

    return manager


def _select_manager(manager_name: str, manager_command: Tuple[str, ...]) -> BaseManager:
    managers = get_supported_managers()

    manager_cls = managers.get(manager_name)
    if manager_cls is None:
        raise ValueError(f"Package manager {manager_name!r} is not supported")

    manager = manager_cls(*manager_command)
    if manager.version() is None:
        raise ValueError(f"Package manager {manager_name!r} is not available")

    return manager


def _managers() -> Dict[str, BaseManager]:
    return {
        name: manager_cls() for name, manager_cls in get_supported_managers().items()
    }


def _first_available(
    managers: Dict[str, BaseManager], scores: Dict[str, Tuple[int, ...]]
) -> Optional[BaseManager]:
    """Available package manager with the highest score. Availability is checked
    in score order because it may be an expensive check.
    """
    for name in sorted(scores, key=lambda name: scores[name], reverse=True):
        manager = managers[name]
        if manager.version():
            logger.debug("Package manager %r selected\n  scores = %s", name, scores)
            return manager
    return None


def _detect_manager() -> Optional[BaseManager]:
    managers = _managers()

    # Select the active manager with the highest priority
    active_managers = {
        name: manager for name, manager in managers.items() if manager.is_active()
    }
    if active_managers:
        scores = {
            name: (manager.PRIORITY,) for name, manager in active_managers.items()
        }
        manager = _first_available(active_managers, scores)
        if manager is not None:
            return manager

    # Infer most likely package manager
    counts = _manager_distribution_count()
    scores = {
        name: (counts.get(name, -1), manager.PRIORITY)
        for name, manager in managers.items()
    }
    return _first_available(managers, scores)


@lru_cache(1)
def _manager_distribution_count() -> Dict[str, int]:
    """Number of installed python distributions per package manager. Distributions
    installed by a tool that is not a supported package manager are not counted.
    """
    managers = get_supported_managers()
    counts: Counter = Counter()
    for dist in current_requirements()["distributions"]:
        for name, manager_cls in managers.items():
            if manager_cls.installed_distribution(dist):
                counts[name] += 1
    return dict(counts)
