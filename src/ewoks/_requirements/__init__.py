"""Workflow requirements."""

import logging
from typing import Tuple

from ewokscore.graph import TaskGraph

from .managers.utils.base import BaseRequirements
from .managers.utils.detect import get_manager
from .metadata.parse import parse_requirements
from .metadata.unknown import unknown_metadata

logger = logging.getLogger(__file__)


def add_requirements(graph: TaskGraph, command: Tuple[str] = tuple()) -> None:
    """Add requirements to a workflow definition in-place."""
    manager = get_manager(command=command)
    requirements = manager.generate_requirements()
    graph.graph.graph["requirements"] = requirements.model_dump()


def install_requirements(
    requirements: BaseRequirements, command: Tuple[str] = tuple()
) -> None:
    """Install workflow requirements."""
    manager = get_manager(manager_name=requirements.manager, command=command)
    manager.install_requirements(requirements)


def get_requirements(graph: TaskGraph) -> BaseRequirements:
    """Extract requirements from a workflow definition."""
    requirements = graph.graph.graph.get("requirements", None)
    if not requirements:
        logger.warning(
            "BaseRequirements field is empty. Trying to extract requirements automatically..."
        )
        requirements = _last_resort_requirements(graph)
        logger.info(f"Extracted the following requirements: {requirements.__info__()}")

    return parse_requirements(requirements)


def _last_resort_requirements(graph: TaskGraph) -> BaseRequirements:
    """Last resort when installing a workflow that does not have requirements:
    guess the requirements from the workflow nodes.
    """
    requirements: set[str] = set()

    for node_id, node in graph.graph.nodes.items():
        task_identifier = node["task_identifier"]
        task_type = node["task_type"]

        if task_type in ("class", "method", "ppfmethod", "ppfport"):
            package = task_identifier.split(".")[0]
            if package in ("__main__", ""):
                logger.warning(
                    f"Could not extract requirements for node {node_id}: the task identifier is a relative import or an import from __main__."
                )
                continue

            requirements.add(package)

        elif task_type == "notebook":
            logger.warning(
                f"Requirement extraction may be incomplete for node {node_id}: {task_type} is only partially supported."
            )
            requirements.add("ewokscore[notebook]")

        elif task_type == "script":
            logger.warning(
                f"Requirement extraction cannot be done for scripts (node {node_id})."
            )
        else:
            logger.warning(
                f"Could not extract requirements for node {node_id}: unsupported task type {task_type}."
            )

    manager = dict(name="pip", version="unknown", requirements=list(requirements))
    requirements = dict(manager=manager, **unknown_metadata())
    return parse_requirements(requirements)
