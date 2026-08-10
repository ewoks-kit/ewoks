import importlib.metadata
import sys
from pathlib import Path
from typing import Dict
from typing import List
from typing import Literal
from typing import Mapping
from typing import Optional
from typing import Sequence

from pydantic import Field

from .utils import process
from .utils import requirements_txt
from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements
from .utils.environment import Environment
from .utils.environment import create_venv
from .utils.files import temporary_files
from .utils.metadata import models

_CONSTRAINTS_FILENAME = "constraints.txt"


class PipVenvManagerInfo(BaseManagerInfo):
    name: Literal["pip-venv"] = Field(
        default="pip-venv",
        description="Environments created with `venv`, requirements installed with `pip`.",
        examples=["pip-venv"],
    )


class PipVenvRequirements(BaseRequirements):
    manager: PipVenvManagerInfo


class PipVenvManager(BaseManager):
    """Creates environments with the `venv` module and installs in them with the
    `pip` module.

    The command is the python interpreter that creates environments. For example
    `PipVenvManager("/path/to/python")`. The current python interpreter is used
    when no command is provided. Unlike other package managers, `venv` cannot
    provide a python version other than the one of this interpreter.
    """

    NAME = "pip-venv"
    PRIORITY = 0
    REQUIREMENTS_MODEL = PipVenvRequirements
    COMMAND_EXAMPLE = "python"
    CAN_INSTALL_IN_PLACE = True

    def __init__(self, *command: str) -> None:
        if not command:
            command = (sys.executable,)
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            return importlib.metadata.version("pip")
        except importlib.metadata.PackageNotFoundError:
            return None

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return False

    @classmethod
    def installed_distribution(cls, distribution: models.Distribution) -> bool:
        """The distribution was installed by this package manager."""
        return "pip" in cls._installer(distribution)

    def create_environment(
        self, location: Path, python_version: Optional[str] = None
    ) -> Environment:
        """
        :raises RuntimeError: creation failed
        """
        environment = self.environment(location)
        create_venv(self._cmd_args[0], environment.prefix, python_version)
        return environment

    def _gather_files(
        self, distributions: List[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        freeze = process.check_output(sys.executable, "-m", "pip", "freeze")
        return {requirements_txt.REQUIREMENTS_FILENAME: freeze}

    def _files_from_distributions(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        requirements = requirements_txt.distributions_requirements(distributions)
        return {requirements_txt.REQUIREMENTS_FILENAME: "\n".join(requirements)}

    def _install_files(
        self, files: Mapping[str, str], environment: Environment
    ) -> None:
        """
        :raises ValueError: no requirements to install
        :raises RuntimeError: installation failed
        """
        requirements = files[requirements_txt.REQUIREMENTS_FILENAME].splitlines()
        self._pip_install(requirements, environment)

    def _add_ewoks(
        self, requirements: BaseRequirements, environment: Environment
    ) -> None:
        self._pip_install(
            ["ewoks"],
            environment,
            constraints=requirements_txt.version_constraints(
                requirements.distributions
            ),
        )

    def _pip_install(
        self,
        requirements: Sequence[str],
        environment: Environment,
        constraints: Optional[Sequence[str]] = None,
    ) -> None:
        """
        :raises ValueError: no requirements to install
        :raises RuntimeError: installation failed
        """
        arguments = requirements_txt.sanitize(requirements)
        if not arguments:
            raise ValueError("No distributions provided to install")

        files = {requirements_txt.REQUIREMENTS_FILENAME: "\n".join(arguments)}
        if constraints:
            files[_CONSTRAINTS_FILENAME] = "\n".join(constraints)

        with temporary_files(files) as directory:
            options = ["-r", directory / requirements_txt.REQUIREMENTS_FILENAME]
            if constraints:
                options += ["--constraint", directory / _CONSTRAINTS_FILENAME]
            process.check_call(
                environment.python,
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                *options,
            )
