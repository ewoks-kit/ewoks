import logging
from collections import Counter
from functools import lru_cache
from typing import Dict
from typing import Optional
from typing import Tuple

from ._supported import get_supported_managers
from .base_manager import BaseManager
from .metadata.from_python import current_requirements

logger = logging.getLogger(__name__)


def get_manager(
    manager_name: Optional[str] = None,
    manager_command: Tuple[str, ...] = tuple(),
) -> BaseManager:
    """
    :raise ValueError: package manager not support or not available
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


def _select_manager(manager_name: str, manager_command: Tuple[str, ...]) -> BaseManager:
    managers = get_supported_managers()

    manager_cls = managers.get(manager_name)
    if manager_cls is None:
        raise ValueError(f"Package manager {manager_name!r} is not supported")

    manager = manager_cls(*manager_command)
    if manager.version() is None:
        raise ValueError(f"Package manager {manager_name!r} is not available")

    return manager


def _detect_manager() -> Optional[BaseManager]:
    # Available package managers
    available_managers = {
        name: manager_cls() for name, manager_cls in get_supported_managers().items()
    }
    available_managers = {
        name: manager
        for name, manager in available_managers.items()
        if manager.version()
    }
    if not available_managers:
        return None

    # Select the active manager with the highest priority
    active_managers = {
        name: manager
        for name, manager in available_managers.items()
        if manager.is_active()
    }
    if active_managers:
        name = max(active_managers, key=lambda name: active_managers[name].PRIORITY)
        manager = active_managers[name]
        logger.debug(
            "Detected active %r package manager\n available = %s\n active = %s",
            name,
            list(available_managers),
            list(active_managers),
        )
        return manager

    # Infer most likely package manager
    counts = _installer_distribution_count()
    if set(counts) & set(available_managers):
        # Use the number of installed distributions as the score
        crit = "distribution count"
        scores = {name: counts.get(name, -1) for name in available_managers}
    else:
        # Use the package manager priority as the score
        crit = "priority"
        scores = {
            name: manager.PRIORITY for name, manager in available_managers.items()
        }

    name = max(scores, key=scores.get)
    logger.debug(
        "Package manager selection based on %s\n  %s",
        crit,
        "\n  ".join(
            f"{k} = {v} {'(SELECTED)' if k == name else ''}" for k, v in scores.items()
        ),
    )
    return available_managers[name]


@lru_cache(1)
def _installer_distribution_count() -> Dict[str, int]:
    counts: Counter = Counter()
    for dist in current_requirements()["distributions"]:
        if dist.installer:
            counts[dist.installer] += 1
    return dict(counts)
