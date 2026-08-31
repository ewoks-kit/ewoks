import json
import logging
import os
import platform
import re
import sys
from pathlib import Path
from typing import Dict
from typing import Literal
from typing import Mapping
from typing import Optional
from typing import Sequence

from pydantic import Field

from .utils import conda_channel
from .utils import requirements_txt
from .utils import toml_dependencies
from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements
from .utils.environment import Environment
from .utils.files import read_files
from .utils.files import temporary_files
from .utils.files import write_files
from .utils.metadata import models

logger = logging.getLogger(__name__)

_MANIFEST_FILENAME = "pixi.toml"
_LOCK_FILENAME = "pixi.lock"
_WORKSPACE_NAME = "ewoks-workflow-requirements"


class PixiManagerInfo(BaseManagerInfo):
    name: Literal["pixi"] = Field(
        default="pixi",
        description="Environments described and created by a `pixi` workspace.",
        examples=["pixi"],
    )


class PixiRequirements(BaseRequirements):
    manager: PixiManagerInfo


class PixiManager(BaseManager):
    """Uses a pixi workspace: `pixi lock` describes an environment with a
    `pixi.toml` and a `pixi.lock` file, `pixi install` reproduces the environment
    from those files. Unlike the python-only package managers this includes
    non-python dependencies.

    The workspace is generated from the installed python distributions instead of
    being taken from a pixi workspace of the current environment. This keeps it
    self-contained: no local project to build.

    The command invokes pixi. For example `PixiManager("/path/to/pixi")`.
    """

    NAME = "pixi"
    PRIORITY = 5
    REQUIREMENTS_MODEL = PixiRequirements
    COMMAND_EXAMPLE = "pixi"
    ENVIRONMENT_SUBDIR = os.path.join(".pixi", "envs", "default")

    def __init__(self, *command: str) -> None:
        if not command:
            command = ("pixi",)
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            output = self._check_output("--version")
        except RuntimeError:
            return None
        # For example "pixi 0.63.2"
        match = re.search(r"(\d+\.\d+(?:\.\d+)*)", output)
        if not match:
            return None
        return match.group(1)

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return (
            "PIXI_PROJECT_ROOT" in os.environ
            or "PIXI_ENVIRONMENT_NAME" in os.environ
            or _is_workspace_environment(Path(sys.prefix))
        )

    def create_environment(
        self, location: Path, python_version: Optional[str] = None
    ) -> Environment:
        """
        :raises RuntimeError: creation failed
        """
        if not python_version:
            python_version = platform.python_version()
        manifest = self._manifest([], python_version)
        write_files(location, {_MANIFEST_FILENAME: manifest})
        self._install_workspace(location)
        return self.environment(location)

    def _files_from_distributions(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        """
        :raises RuntimeError: the requirements cannot be resolved
        """
        requirements = requirements_txt.manifest_requirements(distributions)
        files = {_MANIFEST_FILENAME: self._manifest(requirements, python_version)}

        with temporary_files(files) as directory:
            self._check_call("lock", "--manifest-path", directory / _MANIFEST_FILENAME)
            lock = read_files(directory, _LOCK_FILENAME)

        return {**files, **lock}

    def _install_files(
        self, files: Mapping[str, str], environment: Environment
    ) -> None:
        write_files(environment.location, files)
        self._install_workspace(environment.location)

    def _add_ewoks(
        self, requirements: BaseRequirements, environment: Environment
    ) -> None:
        # The workspace pins all versions so they cannot change
        self._check_call(
            "add",
            "--pypi",
            "ewoks",
            "--manifest-path",
            environment.location / _MANIFEST_FILENAME,
        )

    def _install_workspace(self, location: Path) -> None:
        self._check_call("install", "--manifest-path", location / _MANIFEST_FILENAME)

    def _manifest(self, requirements: Sequence[str], python_version: str) -> str:
        """Content of a `pixi.toml` file with python distributions as pypi
        dependencies.
        """
        pypi_dependencies = "".join(
            f"{line}\n" for line in toml_dependencies.dependency_lines(requirements)
        )
        python = conda_channel.python_specifier(python_version)
        return f"""[workspace]
name = {json.dumps(_WORKSPACE_NAME)}
channels = ["conda-forge"]
platforms = [{json.dumps(self._platform())}]

[dependencies]
python = {json.dumps(python)}

[pypi-dependencies]
{pypi_dependencies}"""

    def _platform(self) -> str:
        """Platform of the current environment, for example `linux-64`.

        :raises RuntimeError: platform unknown
        """
        output = self._check_output("info", "--json")
        try:
            return json.loads(output)["platform"]
        except (ValueError, KeyError):
            raise RuntimeError("Cannot determine the pixi platform") from None


def _is_workspace_environment(prefix: Path) -> bool:
    """Environment is managed by a pixi workspace."""
    parts = prefix.parts
    return len(parts) > 2 and parts[-3] == ".pixi" and parts[-2] == "envs"
