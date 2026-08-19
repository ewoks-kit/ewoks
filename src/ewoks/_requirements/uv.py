import json
import os
import re
import sys
from pathlib import Path
from typing import Dict
from typing import Literal
from typing import Mapping
from typing import Optional
from typing import Sequence

from pydantic import Field

from .utils import requirements_txt
from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements
from .utils.environment import Environment
from .utils.files import read_files
from .utils.files import temporary_files
from .utils.files import write_files
from .utils.metadata import models

_PYPROJECT_FILENAME = "pyproject.toml"
_LOCK_FILENAME = "uv.lock"
_CONSTRAINTS_FILENAME = "constraints.txt"
_PROJECT_NAME = "ewoks-workflow-requirements"


class UvManagerInfo(BaseManagerInfo):
    name: Literal["uv"] = Field(
        default="uv",
        description="Environments described and created by a `uv` project.",
        examples=["uv"],
    )


class UvRequirements(BaseRequirements):
    manager: UvManagerInfo


class UvManager(BaseManager):
    """Uses the `uv` project interface: `uv lock` describes an environment with a
    `pyproject.toml` and a `uv.lock` file, `uv sync` reproduces the environment
    from those files.

    The project is generated from the installed python distributions instead of
    being taken from a `uv` project of the current environment. This keeps it
    self-contained: no workspace members and no local project to build.

    The command invokes uv. For example `UvManager("/path/to/uv")`.
    """

    NAME = "uv"
    PRIORITY = 1
    REQUIREMENTS_MODEL = UvRequirements
    COMMAND_EXAMPLE = "uv"
    ENVIRONMENT_SUBDIR = ".venv"
    CAN_INSTALL_IN_PLACE = True

    def __init__(self, *command: str) -> None:
        if not command:
            command = ("uv",)
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            output = self._check_output("--version")
        except RuntimeError:
            return None
        # For example "uv 0.12.1 (x86_64-unknown-linux-gnu)"
        match = re.search(r"(\d+\.\d+(?:\.\d+)*)", output)
        if not match:
            return None
        return match.group(1)

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return (
            "UV" in os.environ
            or _created_by_uv(Path(sys.prefix))
            or _is_project(Path(sys.prefix).parent)
        )

    def create_environment(
        self, location: Path, python_version: Optional[str] = None
    ) -> Environment:
        """
        :raises RuntimeError: creation failed
        """
        environment = self.environment(location)
        # Without a python request, uv selects one of its own interpreters
        python = python_version or sys.executable
        self._check_call("venv", "--python", python, environment.prefix)
        return environment

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
            self._check_call("lock", "--project", directory)
            lock = read_files(directory, _LOCK_FILENAME)

        return {**files, **lock}

    def _install_files(
        self, files: Mapping[str, str], environment: Environment
    ) -> None:
        if self._owns(environment):
            write_files(environment.location, files)
            self._sync(environment.location)
            return

        # An environment that is not a uv project can only be filled through the
        # pip-compatible interface of uv: `uv sync` always targets '<project>/.venv'
        with temporary_files(files) as directory:
            filename = directory / requirements_txt.REQUIREMENTS_FILENAME
            self._check_call(
                "export",
                "--frozen",
                "--no-hashes",
                "--quiet",
                "--project",
                directory,
                "--output-file",
                filename,
            )
            self._pip_install(environment, "-r", filename)

    def _add_ewoks(
        self, requirements: BaseRequirements, environment: Environment
    ) -> None:
        if self._owns(environment):
            # The project pins all versions so they cannot change
            self._check_call("add", "--project", environment.location, "ewoks")
            return

        constraints = requirements_txt.version_constraints(requirements.distributions)
        if not constraints:
            self._pip_install(environment, "ewoks")
            return
        with temporary_files({_CONSTRAINTS_FILENAME: "\n".join(constraints)}) as tmpdir:
            self._pip_install(
                environment,
                "ewoks",
                "--constraint",
                tmpdir / _CONSTRAINTS_FILENAME,
            )

    def _sync(self, location: Path) -> None:
        self._check_call(
            "sync", "--frozen", "--no-install-project", "--project", location
        )

    def _pip_install(self, environment: Environment, *arguments: str) -> None:
        self._check_call(
            "pip",
            "install",
            "--no-cache",
            "--python",
            environment.python,
            *arguments,
        )


def _pyproject(requirements: Sequence[str], python_version: str) -> str:
    """Content of a `pyproject.toml` file for a project that is not a package."""
    dependencies = "".join(f"    {json.dumps(req)},\n" for req in requirements)
    if python_version:
        python = f'requires-python = "=={python_version}"\n'
    else:
        python = ""
    return f"""[project]
name = {json.dumps(_PROJECT_NAME)}
version = "0.0.0"
{python}dependencies = [
{dependencies}]

[tool.uv]
package = false
"""


def _is_project(directory: Path) -> bool:
    """Directory is a uv project."""
    return (directory / _LOCK_FILENAME).is_file()


def _created_by_uv(prefix: Path) -> bool:
    """Environment is a virtual environment created by uv."""
    try:
        with open(prefix / "pyvenv.cfg", "r", encoding="utf-8") as fh:
            return any(line.split("=")[0].strip() == "uv" for line in fh)
    except OSError:
        return False
