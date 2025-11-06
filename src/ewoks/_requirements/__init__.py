"""Workflow requirements."""

import logging
from typing import Tuple

from ewokscore.graph import TaskGraph

from .managers.utils.base import BaseRequirements
from .managers.utils.detect import get_manager
from .metadata import parse
from .metadata.gather import last_resort

logger = logging.getLogger(__file__)


def add_requirements(graph: TaskGraph, command: Tuple[str, ...] = tuple()) -> None:
    """Add requirements to a workflow definition in-place."""
    manager = get_manager(command=command)
    requirements = manager.gather_requirements()
    graph.graph.graph["requirements"] = requirements.model_dump()


def get_requirements(graph: TaskGraph) -> BaseRequirements:
    """Extract requirements from a workflow definition."""
    requirements = graph.graph.graph.get("requirements", None)
    no_requirements = not requirements

    if no_requirements:
        logger.warning(
            "BaseRequirements field is empty. Trying to extract requirements automatically..."
        )
        requirements = last_resort.last_resort_requirements(graph)

    requirements = parse.parse_requirements(requirements)

    if no_requirements:
        logger.info(f"Extracted the following requirements: {requirements.__info__()}")

    return requirements


def install_requirements(
    requirements: BaseRequirements, command: Tuple[str, ...] = tuple()
) -> None:
    """Install workflow requirements."""
    manager = get_manager(manager_name=requirements.manager.name, command=command)
    manager.install_requirements(requirements)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    import time
    from pprint import pprint

    t0 = time.perf_counter()

    try:
        manager = get_manager(manager_name=None)
        requirements = manager.gather_requirements()

        print()
        print("Model:")
        pprint(requirements.model_dump())
    finally:
        print("Freeze time:", time.perf_counter() - t0)

    pip_freeze = requirements.manager.freeze

    dists_freeze = manager.freeze_distributions(requirements)
    dists_freeze = [s for s in dists_freeze if not s.startswith("#")]

    print()
    print("pip freeze has these extra's:")
    pprint(set(pip_freeze) - set(dists_freeze))

    print()
    print("native freeze has these extra's:")
    pprint(set(dists_freeze) - set(pip_freeze))
