import logging
from abc import abstractmethod
from pathlib import Path
from textwrap import indent
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Union

from pydantic import Field

from . import process
from .environment import Environment
from .metadata import models
from .metadata.from_python import current_requirements

logger = logging.getLogger(__name__)

EWOKS_ENVIRONMENTS_ROOT = Path("~", ".ewoks", "envs")
"""Root directory of named environments for package managers that do not create
them in a directory of their own."""


class BaseManagerInfo(models.BaseModel):
    name: str = Field(
        description="Package manager that generated the requirements.",
        examples=["pip-venv", "uv"],
    )
    version: str = Field(
        description="Version of the package manager.", examples=["25.0.1"]
    )
    files: Dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Content of the files the package manager needs to reproduce the "
            "environment: 'requirements.txt' for pip-venv, 'pyproject.toml' and "
            "'uv.lock' for uv. Empty when the package manager could not generate "
            "them."
        ),
        examples=[{"requirements.txt": "ewoks==7.0.0\nnetworkx==3.4.2\n"}],
    )


class BaseRequirements(models.BaseModel):
    system: models.SystemInfo = Field(
        description="Operating system on which the requirements were generated."
    )
    python: models.PythonInfo = Field(
        description="Python interpreter for which the requirements were generated."
    )
    distributions: List[models.Distribution] = Field(
        description=(
            "Installed python distributions. Any package manager can reproduce the "
            "environment from this list, also one that does not understand the "
            "files of the package manager that generated the requirements."
        ),
        examples=[[{"name": "networkx", "version": "3.4.2"}]],
    )
    manager: BaseManagerInfo = Field(
        description="Package manager that generated the requirements."
    )

    def __info__(self) -> str:
        return f"{self.__files_info__()}\n{self.__distributions_info__()}"

    def __files_info__(self) -> str:
        """The package manager with the content of the files it needs to reproduce
        the environment."""
        info = (
            f"Manager: {self.manager.name} ({self.manager.version}) "
            f"python={self.python.version} "
            f"distributions={len(self.distributions)}"
        )
        for filename in sorted(self.manager.files):
            content = indent(self.manager.files[filename].strip(), "  ")
            info = f"{info}\n\n{filename}:\n{content}"
        return info

    def __distributions_info__(self) -> str:
        """The installed python distributions."""
        distributions = "\n  ".join(
            f"{dist.name}=={dist.version}" for dist in self.distributions
        )
        return f"Distributions:\n  {distributions}"


class BaseManager:
    """Defines the interface all package managers must implement.

    If `MyManager` is an implementation of this interface then the requirements
    of the current python environment can be obtained like this:

    .. code-block:: python

        manager = MyManager()
        requirements = manager.gather_requirements()

    Those requirements can be reproduced in another python environment like this:

    .. code-block:: python

        manager = MyManager()
        environment = manager.create_environment(Path("/path/to/environment"))
        if manager.is_native(requirements, environment):
            manager.install_files(requirements, environment)
        else:
            manager.install_distributions(requirements, environment)

    An implementation provides `version`, `is_active`, `create_environment`,
    `_files_from_distributions`, `_install_files` and `_add_ewoks`. Package managers
    that can inspect a python environment also override `_gather_files`. Package
    managers that keep named environments in a directory of their own also override
    `environments_root`. Package managers that are not named after the tool that
    installs the distributions also override `installed_distribution`.
    """

    NAME = NotImplemented
    PRIORITY = NotImplemented
    REQUIREMENTS_MODEL = NotImplemented
    COMMAND_EXAMPLE = NotImplemented  # example of an associated shell command
    ENVIRONMENT_SUBDIR = ""  # environment prefix relative to the location
    CAN_INSTALL_IN_PLACE = False  # can install in the current environment

    def __init__(self, *command: str) -> None:
        if not command:
            raise ValueError(f"{type(self).__name__} needs an associated shell command")
        self._cmd_args = command

    def __repr__(self):
        return f"{type(self).__name__}({', '.join(self._cmd_args)})"

    @abstractmethod
    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Manager is explicitly active."""
        pass

    @classmethod
    def installed_distribution(cls, distribution: models.Distribution) -> bool:
        """The distribution was installed by this package manager."""
        return cls.NAME in cls._installer(distribution)

    @staticmethod
    def _installer(distribution: models.Distribution) -> str:
        """Tool that installed the distribution. It can contain more than the name
        of the tool, for example its version.
        """
        return (distribution.installer or "").lower()

    def gather_requirements(self) -> BaseRequirements:
        """
        Return requirements associated to the current python environment.

        :raises RuntimeError: package manager not available
        """
        manager_version = self.version()
        if manager_version is None:
            raise RuntimeError(f"{self.NAME!r} is not available")

        metadata = current_requirements()
        files = self._gather_files(
            metadata["distributions"], metadata["python"]["version"]
        )

        manager = dict(name=self.NAME, version=manager_version, files=files)
        return self.REQUIREMENTS_MODEL(manager=manager, **metadata)

    def environment(self, location: Union[str, Path]) -> Environment:
        """Environment the manager creates at this location."""
        return Environment.at_location(location, self.ENVIRONMENT_SUBDIR)

    def environment_location(
        self, name: str, root: Optional[Union[str, Path]] = None
    ) -> Path:
        """Location of the environment with this name, inside a root directory of
        the user or inside the root directory of this package manager.
        """
        return Path(root or self.environments_root()).expanduser() / name

    def environments_root(self) -> Path:
        """Root directory in which the package manager creates named environments.
        Package managers that create an environment wherever they are told to (venv
        and uv) use a directory of ewoks.
        """
        return EWOKS_ENVIRONMENTS_ROOT

    @abstractmethod
    def create_environment(
        self, location: Path, python_version: Optional[str] = None
    ) -> Environment:
        """Create an empty python environment.

        :raises RuntimeError: creation failed
        """
        pass

    def is_native(
        self, requirements: BaseRequirements, environment: Environment
    ) -> bool:
        """The files of the requirements are the files of this package manager and
        the environment has the layout this package manager creates.
        """
        return (
            isinstance(requirements, self.REQUIREMENTS_MODEL)
            and bool(requirements.manager.files)
            and self._owns(environment)
        )

    def install_files(
        self, requirements: BaseRequirements, environment: Environment
    ) -> None:
        """Install the files of the requirements in an existing environment. The
        requirements must be native (see `is_native`).

        :raises RuntimeError: installation failed
        """
        try:
            self._install_files(requirements.manager.files, environment)
        except Exception as ex:
            logger.error(
                "%s: failed to install the requirement files (%s)",
                type(self).__name__,
                ex,
            )
            raise

    def install_distributions(
        self, requirements: BaseRequirements, environment: Environment
    ) -> None:
        """Install the python distributions of the requirements in an existing
        environment.

        :raises ValueError: no distributions provided to install
        :raises RuntimeError: installation failed
        """
        if not requirements.distributions:
            raise ValueError("No distributions provided to install")
        # Requirements that do not specify a python version are described for the
        # python version of the environment they are installed in
        python_version = requirements.python.version or environment.python_version()
        try:
            files = self._files_from_distributions(
                requirements.distributions, python_version
            )
            self._install_files(files, environment)
        except Exception as ex:
            logger.error(
                "%s: failed to install the python distributions (%s)",
                type(self).__name__,
                ex,
            )
            raise

    def ensure_ewoks(
        self, requirements: BaseRequirements, environment: Environment
    ) -> None:
        """Install ewoks in an existing environment without changing the versions
        of the requirements.

        :raises RuntimeError: installation failed
        """
        if environment.distribution_version("ewoks"):
            return
        logger.info("Add ewoks to %s", environment.location)
        self._add_ewoks(requirements, environment)

    def _owns(self, environment: Environment) -> bool:
        """The environment has the layout this package manager creates."""
        return environment.python == self.environment(environment.location).python

    def _gather_files(
        self, distributions: List[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        """Files that describe the current python environment. Package managers
        that can inspect an environment override this.
        """
        try:
            return self._files_from_distributions(distributions, python_version)
        except RuntimeError as ex:
            logger.warning(
                "%s cannot describe the current python environment (%s). It will be "
                "reproduced from the installed python distributions.",
                self.NAME,
                ex,
            )
            return dict()

    @abstractmethod
    def _files_from_distributions(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        """Files the package manager needs to install these python distributions.

        :raises RuntimeError: the files cannot be generated
        """
        pass

    @abstractmethod
    def _install_files(
        self, files: Mapping[str, str], environment: Environment
    ) -> None:
        """Install the files of the package manager in an existing environment.

        :raises RuntimeError: installation failed
        """
        pass

    @abstractmethod
    def _add_ewoks(
        self, requirements: BaseRequirements, environment: Environment
    ) -> None:
        """Install ewoks in an existing environment without changing the versions
        of the requirements.

        :raises RuntimeError: installation failed
        """
        pass

    def _check_output(
        self, *args: Union[str, Path], extra_env: Optional[Mapping[str, str]] = None
    ) -> str:
        return process.check_output(*self._cmd_args, *args, extra_env=extra_env)

    def _check_call(
        self, *args: Union[str, Path], extra_env: Optional[Mapping[str, str]] = None
    ) -> None:
        process.check_call(*self._cmd_args, *args, extra_env=extra_env)
