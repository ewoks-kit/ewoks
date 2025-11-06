import logging
from collections import Counter
from functools import lru_cache
from typing import Dict
from typing import Optional
from typing import Tuple

from ...metadata.gather import installed
from .base import BaseManager
from .supported import ManagerInfo
from .supported import get_supported_managers

logger = logging.getLogger(__name__)


def get_manager(
    manager_name: Optional[str] = None,
    command: Tuple[str, ...] = tuple(),
) -> BaseManager:
    """
    :raise ValueError: package manager not support
    :raise RuntimeError: no package manager available
    """
    if manager_name:
        managers = get_supported_managers()

        info = managers.get(manager_name)
        if info is None:
            raise ValueError(f"Package manager {manager_name!r} is not supported")

        return info.manager_type(*command)

    info = _detect_manager()
    if info is None:
        raise RuntimeError("No known package manager installed or available")

    return info.manager_type(*command)


def _detect_manager() -> Optional[ManagerInfo]:
    # Available package managers
    available_managers = {
        name: info for name, info in get_supported_managers().items() if info.version
    }
    if not available_managers:
        return None

    # Select the active manager with the highest priority
    active_managers = {
        name: info for name, info in available_managers.items() if info.is_active
    }
    if active_managers:
        name = max(active_managers, key=lambda name: active_managers[name].priority)
        info = active_managers[name]
        logger.debug(
            "Detected active %r package manager\n available = %s\n active = %s",
            name,
            list(available_managers),
            list(active_managers),
        )
        return info

    # Infer most likely package manager
    counts = _installer_distribution_count()
    if set(counts) & set(available_managers):
        # Use the number of installed distibutions as the score
        crit = "distribution count"
        scores = {name: counts.get(name, -1) for name in available_managers}
    else:
        # Use the package manager priority as the score
        crit = "priority"
        scores = {name: info.priority for name, info in available_managers.items()}

    name = max(scores, key=scores.get)
    logger.debug(
        "Package manager selection based on %s\n  %s",
        crit,
        "\n  ".join(
            f"{k} = {v} {'(SELECTED)' if k == name else ''}" for k, v in scores.items()
        ),
    )
    return available_managers[name]


@lru_cache
def _installer_distribution_count() -> Dict[str, int]:
    counts: Counter = Counter()
    for dist in installed.distributions():
        if dist.installer:
            counts[dist.installer] += 1
    return dict(counts)
