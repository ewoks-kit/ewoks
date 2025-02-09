import logging
import subprocess
import sys
from typing import List

from ewokscore.graph import TaskGraph

logger = logging.getLogger(__file__)


def extract_requirements(graph: TaskGraph) -> List[str]:
    imports: set[str] = set()

    for node_id, node in graph.graph.nodes.items():
        task_identifier = node["task_identifier"]
        task_type = node["task_type"]

        if (
            task_type == "class"
            or task_type == "method"
            or task_type == "ppfmethod"
            or task_type == "ppfport"
        ):
            package = task_identifier.split(".")[0]
            if package == "__main__" or "":
                logger.warning(
                    f"Could not extract requirements for node {node_id}: the task identifier is a relative import or a import from __main__."
                )
                continue

            imports.add(package)

        elif task_type == "notebook":
            logger.warning(
                f"Requirement extraction may be incomplete for node {node_id}: {task_type} is only partially supported."
            )
            imports.add("ewokscore[notebook]")

        elif task_type == "script":
            logger.warning(
                f"Requirement extraction cannot be done for scripts (node {node_id})."
            )
        else:
            logger.warning(
                f"Could not extract requirements for node {node_id}: unsupported task type {task_type}."
            )

    return list(imports)


def save_current_env_as_requirements(graph: TaskGraph) -> TaskGraph:

    freeze_output = subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze"], text=True
    )
    requirements = freeze_output.strip().split("\n")

    graph.graph.graph["requirements"] = requirements

    return graph
