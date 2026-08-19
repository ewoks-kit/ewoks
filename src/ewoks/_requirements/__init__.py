"""Workflow requirements."""

import logging
import re
import shutil
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

from ewokscore.graph import TaskGraph
from ewokscore.hashing import uhash

from .utils import parse
from .utils._supported import get_supported_managers
from .utils.base_manager import BaseRequirements
from .utils.detect import get_in_place_installer
from .utils.detect import get_installer
from .utils.detect import get_manager
from .utils.environment import Environment
from .utils.metadata import last_resort

logger = logging.getLogger(__file__)

_NO_GRAPH_ID = "notspecified"
"""Identifier of a workflow that does not have one."""


def supported_managers() -> Dict[str, str]:
    """Names of the supported package managers with an example command for each."""
    return {
        name: manager_cls.COMMAND_EXAMPLE
        for name, manager_cls in get_supported_managers().items()
    }


def managers_supporting_in_place() -> Tuple[str, ...]:
    """Names of the package managers that can install in the current environment."""
    return tuple(
        name
        for name, manager_cls in get_supported_managers().items()
        if manager_cls.CAN_INSTALL_IN_PLACE
    )


def add_requirements(
    graph: TaskGraph,
    manager_name: Optional[str] = None,
    manager_command: Tuple[str, ...] = tuple(),
) -> str:
    """Add requirements to a workflow definition in-place. Returns the name of the
    package manager that generated them.
    """
    manager = get_manager(manager_name=manager_name, manager_command=manager_command)
    requirements = manager.gather_requirements()
    graph.graph.graph["requirements"] = requirements.model_dump()
    return manager.NAME


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


def environment_name(graph: TaskGraph) -> str:
    """Name of the python environment of a workflow: its identifier, or a hash of
    the workflow when it does not have one.
    """
    name = str(graph.graph_id)
    if name == _NO_GRAPH_ID:
        name = str(uhash(graph.serialize()))[:16]
    return re.sub(r"[^\w.-]", "_", name)[:64] or _NO_GRAPH_ID


def install_requirements(
    requirements: BaseRequirements,
    env_name: Optional[str] = None,
    env_root: Optional[Union[str, Path]] = None,
    manager_name: Optional[str] = None,
    manager_command: Tuple[str, ...] = tuple(),
    python_version: Optional[str] = None,
    ensure_ewoks: bool = False,
    clean: bool = False,
    confirm: Optional[Callable[[str], None]] = None,
) -> Environment:
    """Install workflow requirements in a python environment named `env_name`,
    created inside `env_root` or inside the root directory of the package manager,
    or in the current python environment when no name is provided. An environment
    that already exists is installed in, or removed first when `clean`.
    The files of the package manager are installed when the requirements provide
    them, the installed python distributions otherwise or when that installation
    failed. `ensure_ewoks` adds ewoks itself when the requirements do not contain it.
    `confirm` is called with a description of an installation or a removal before
    it starts.

    :raises ValueError: no environment name, the package manager cannot install in
                        the current environment or the environment to remove is not
                        a python environment
    :raises RuntimeError: environment creation or installation failed
    """
    if env_name is None:
        if env_root:
            raise ValueError("An environment root requires an environment name")
        if clean:
            raise ValueError("Cleaning requires an environment name")

    manager = get_installer(
        requirements, manager_name=manager_name, manager_command=manager_command
    )

    if env_name is None:
        if not manager.CAN_INSTALL_IN_PLACE:
            if manager_name:
                raise ValueError(
                    f"Package manager {manager_name!r} cannot install in the current "
                    "python environment"
                )
            manager = get_in_place_installer()
        location = None
        remove = False
        environment = Environment.current()
        destination = "the current python environment"
    else:
        location = manager.environment_location(env_name, env_root)
        if python_version is None:
            python_version = requirements.python.version or None
        environment = manager.environment(location)
        remove = clean and location.exists()
        if remove:
            _assert_environment(location)
        if location.exists() and not remove:
            logger.warning(
                "The python environment in '%s' already exists: the requirements "
                "are installed in it",
                location,
            )
            destination = f"the existing python environment in '{location}'"
        else:
            destination = f"a new python environment in '{location}'"

    # The environment is created after the confirmation of the first installation
    native = manager.is_native(requirements, environment)
    if native:
        _confirm(
            confirm,
            requirements.__files_info__(),
            f"This will install the files of the {manager.NAME} package manager "
            f"above in {destination}.",
        )
    else:
        logger.warning(
            "The requirements do not provide files that the %r package manager can "
            "install. The installed python distributions are installed instead.",
            manager.NAME,
        )
        _confirm(
            confirm,
            requirements.__distributions_info__(),
            f"The requirements do not provide files that the {manager.NAME} package "
            "manager can install. This will install the python distributions above "
            f"in {destination} instead.",
        )

    if location is not None:
        if remove:
            if confirm is not None:
                confirm(
                    f"This will remove the existing python environment in '{location}'."
                )
            shutil.rmtree(location)
        environment = manager.create_environment(location, python_version)

    installed = False
    if native:
        try:
            manager.install_files(requirements, environment)
            installed = True
        except Exception:
            logger.exception(
                "Continue with the installed python distributions after failure to "
                "install the files of the %r package manager",
                manager.NAME,
            )
            _confirm(
                confirm,
                requirements.__distributions_info__(),
                f"Installing the files of the {manager.NAME} package manager failed. "
                "This will install the python distributions above in "
                f"{destination} instead.",
            )

    if not installed:
        manager.install_distributions(requirements, environment)

    if ensure_ewoks:
        manager.ensure_ewoks(requirements, environment)

    return environment


def _assert_environment(location: Path) -> None:
    """Only a python environment is removed to create a new one.

    :raises ValueError: the location is not a python environment
    """
    try:
        Environment.from_location(location)
    except ValueError:
        raise ValueError(
            f"'{location}' is not a python environment: remove it yourself to "
            "create an environment there"
        ) from None


def _confirm(
    confirm: Optional[Callable[[str], None]], content: str, action: str
) -> None:
    """Describe an installation and let `confirm` accept or refuse it."""
    if confirm is None:
        return
    confirm(f"{content}\n\n{action}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    import time
    from pprint import pprint

    from .utils import requirements_txt

    t0 = time.perf_counter()

    try:
        manager = get_manager(manager_name="pip-venv")
        requirements = manager.gather_requirements()

        print()
        print("Model:")
        pprint(requirements.model_dump())
    finally:
        print("Freeze time:", time.perf_counter() - t0)

    pip_freeze = requirements.manager.files[
        requirements_txt.REQUIREMENTS_FILENAME
    ].splitlines()

    dists_freeze = requirements_txt.distributions_requirements(
        requirements.distributions
    )
    dists_freeze = [s for s in dists_freeze if not s.startswith("#")]

    print()
    print("pip freeze has these extra's:")
    pprint(set(pip_freeze) - set(dists_freeze))

    print()
    print("native freeze has these extra's:")
    pprint(set(dists_freeze) - set(pip_freeze))
