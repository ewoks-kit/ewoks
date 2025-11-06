import logging
from typing import Any
from typing import Dict

from ewokscore.graph import TaskGraph

from . import pip_freeze

logger = logging.getLogger(__name__)


def last_resort_requirements(graph: TaskGraph) -> Dict[str, Any]:
    """Last resort when installing a workflow that does not have requirements:
    guess the requirements from the workflow nodes.
    """
    freeze: set[str] = set()

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

            freeze.add(package)

        elif task_type == "notebook":
            logger.warning(
                f"Requirement extraction may be incomplete for node {node_id}: {task_type} is only partially supported."
            )
            freeze.add("ewokscore[notebook]")

        elif task_type == "script":
            logger.warning(
                f"Requirement extraction cannot be done for scripts (node {node_id})."
            )
        else:
            logger.warning(
                f"Could not extract requirements for node {node_id}: unsupported task type {task_type}."
            )

    return pip_freeze.pip_freeze_requirements(list(freeze))
