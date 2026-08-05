"""Workflow requirements."""

import logging
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

from ewokscore.graph import TaskGraph

from .utils import parse
from .utils._supported import get_supported_managers
from .utils.base_manager import BaseRequirements
from .utils.detect import get_manager
from .utils.metadata import last_resort

logger = logging.getLogger(__file__)


def supported_managers() -> Dict[str, str]:
    """Names of the supported package managers with an example command for each."""
    return {
        name: manager_cls.COMMAND_EXAMPLE
        for name, manager_cls in get_supported_managers().items()
    }


def add_requirements(
    graph: TaskGraph,
    manager_name: Optional[str] = None,
    manager_command: Tuple[str, ...] = tuple(),
) -> None:
    """Add requirements to a workflow definition in-place."""
    manager = get_manager(manager_name=manager_name, manager_command=manager_command)
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
    requirements: BaseRequirements,
    manager_name: Optional[str] = None,
    manager_command: Union[None, str, Tuple[str, ...]] = None,
) -> None:
    """Install workflow requirements."""

    if manager_command and not manager_name:
        raise ValueError(
            f"Provide 'manager_name' associated to command {manager_command}"
        )

    try:
        if manager_name:
            raise ValueError("Ignore package manager used to generate the requirements")
        else:
            manager = get_manager(manager_name=requirements.manager.name)
    except ValueError:
        manager = get_manager(
            manager_name=manager_name, manager_command=manager_command
        )

    manager.install_requirements(requirements)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    import time
    from pprint import pprint

    t0 = time.perf_counter()

    try:
        manager = get_manager(manager_name="pip")
        requirements = manager.gather_requirements()

        print()
        print("Model:")
        pprint(requirements.model_dump())
    finally:
        print("Freeze time:", time.perf_counter() - t0)

    pip_freeze = requirements.manager.freeze

    dists_freeze = manager._freeze_distributions(requirements)
    dists_freeze = [s for s in dists_freeze if not s.startswith("#")]

    print()
    print("pip freeze has these extra's:")
    pprint(set(pip_freeze) - set(dists_freeze))

    print()
    print("native freeze has these extra's:")
    pprint(set(dists_freeze) - set(pip_freeze))
