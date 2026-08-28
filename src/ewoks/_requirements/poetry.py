import json
import logging
import os
import platform
import re
import shutil
import sys
from pathlib import Path
from typing import Dict
from typing import Literal
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from pydantic import Field

from .utils import requirements_txt
from .utils import toml_dependencies
from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements
from .utils.environment import Environment
from .utils.environment import interpreter_version
from .utils.files import read_files
from .utils.files import temporary_files
from .utils.files import write_files
from .utils.metadata import models

logger = logging.getLogger(__name__)

_MINIMUM_VERSION = (1, 8)

_PYPROJECT_FILENAME = "pyproject.toml"
_LOCK_FILENAME = "poetry.lock"


class PoetryManagerInfo(BaseManagerInfo):
    name: Literal["poetry"] = Field(
        default="poetry",
        description="Environments described and created by a `poetry` project.",
        examples=["poetry"],
    )


class PoetryRequirements(BaseRequirements):
    manager: PoetryManagerInfo


class PoetryManager(BaseManager):
    """Uses a poetry project: `poetry lock` describes an environment with a
    `pyproject.toml` and a `poetry.lock` file, `poetry install` reproduces the
    environment from those files.

    The project is generated from the installed python distributions instead of
    being taken from a poetry project of the current environment. This keeps it
    self-contained: no local project to build.

    Environments are created with `poetry env use`, which needs an interpreter of
    the requested python version because poetry cannot install one.

    The command invokes poetry. For example `PoetryManager("/path/to/poetry")`.
    """

    NAME = "poetry"
    PRIORITY = 2
    REQUIREMENTS_MODEL = PoetryRequirements
    COMMAND_EXAMPLE = "poetry"
    ENVIRONMENT_SUBDIR = ".venv"

    def __init__(self, *command: str) -> None:
        if not command:
            command = ("poetry",)
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            output = self._check_output(
                "--version", extra_env=_python_env(sys.executable)
            )
        except RuntimeError:
            return None
        # For example "Poetry (version 2.4.1)"
        match = re.search(r"(\d+\.\d+(?:\.\d+)*)", output)
        if not match:
            return None
        version = match.group(1)
        if _version_tuple(version) < _MINIMUM_VERSION:
            # Older versions have no project without a package to build
            logger.warning(
                "Poetry %s is not supported: version %s or later is required",
                version,
                ".".join(str(part) for part in _MINIMUM_VERSION),
            )
            return None
        return version

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return "POETRY_ACTIVE" in os.environ or _is_project(Path(sys.prefix).parent)

    def create_environment(
        self, location: Path, python_version: Optional[str] = None
    ) -> Environment:
        """
        :raises RuntimeError: creation failed
        """
        # The project that poetry attaches the environment to. Its python version
        # is not constrained yet: the requirements provide it when they are installed.
        write_files(location, {_PYPROJECT_FILENAME: _pyproject([], "")})
        self._check_call(
            "-C",
            location,
            "env",
            "use",
            _base_python(python_version),
            extra_env=_python_env(sys.executable),
        )
        return self.environment(location)

    def environments_root(self) -> Path:
        """Directory in which poetry creates the environments of projects that do
        not contain them (`virtualenvs.path`).
        """
        try:
            root = Path(
                self._check_output(
                    "config", "virtualenvs.path", extra_env=_python_env(sys.executable)
                ).strip()
            )
            if not root.is_absolute():
                raise RuntimeError(f"{str(root)!r} is not a directory")
            return root
        except RuntimeError as ex:
            logger.warning(
                "Cannot determine where poetry creates environments (%s)", ex
            )
            return super().environments_root()

    def _files_from_distributions(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        """
        :raises RuntimeError: the requirements cannot be resolved
        """
        pyproject = _pyproject(
            requirements_txt.manifest_requirements(distributions), python_version
        )
        files = {_PYPROJECT_FILENAME: pyproject}

        with temporary_files(files) as directory:
            self._check_call(
                "-C", directory, "lock", extra_env=_python_env(sys.executable)
            )
            lock = read_files(directory, _LOCK_FILENAME)

        return {**files, **lock}

    def _install_files(
        self, files: Mapping[str, str], environment: Environment
    ) -> None:
        write_files(environment.location, files)
        self._check_call(
            "-C",
            environment.location,
            "install",
            "--no-root",
            extra_env=_python_env(environment.python),
        )

    def _add_ewoks(
        self, requirements: BaseRequirements, environment: Environment
    ) -> None:
        # The project pins all versions so they cannot change
        self._check_call(
            "-C",
            environment.location,
            "add",
            "ewoks",
            extra_env=_python_env(environment.python),
        )


def _pyproject(requirements: Sequence[str], python_version: str) -> str:
    """Content of a `pyproject.toml` file for a project that is not a package.

    The dependencies are declared in the `tool.poetry` section instead of a PEP 621
    `project` section, which poetry only understands since version 2.
    """
    python = f"=={python_version}" if python_version else "*"
    dependencies = "".join(
        f"{line}\n" for line in toml_dependencies.dependency_lines(requirements)
    )
    return f"""[tool.poetry]
package-mode = false

[tool.poetry.dependencies]
python = {json.dumps(python)}
{dependencies}"""


def _base_python(python_version: Optional[str]) -> Path:
    """Interpreter poetry creates an environment with."""
    if not python_version or python_version == platform.python_version():
        return Path(sys.executable)
    major_minor = ".".join(python_version.split(".")[:2])
    python = Path(shutil.which(f"python{major_minor}") or sys.executable)
    version = interpreter_version(python)
    if version != python_version:
        logger.warning(
            "poetry cannot provide python %s: creating the environment with "
            "python %s instead",
            python_version,
            version,
        )
    return python


def _version_tuple(version: str) -> Tuple[int, ...]:
    return tuple(int(part) for part in version.split(".") if part.isdigit())


def _python_env(python: Union[str, Path]) -> Dict[str, str]:
    """Poetry searches `PATH` for a python interpreter, which is not necessarily
    a working one. Make sure it finds this interpreter first. The environment of
    a project is the `.venv` directory inside it.
    """
    path = os.environ.get("PATH", "")
    return {
        "PATH": os.pathsep.join([str(Path(python).parent), path]),
        "POETRY_VIRTUALENVS_IN_PROJECT": "true",
    }


def _is_project(directory: Path) -> bool:
    """Directory is a poetry project."""
    return (directory / _LOCK_FILENAME).is_file()
