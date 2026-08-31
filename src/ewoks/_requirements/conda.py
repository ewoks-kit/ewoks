import json
import logging
import os
import platform
import re
import shutil
import sys
from pathlib import Path
from typing import Dict
from typing import List
from typing import Literal
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple

from pydantic import Field

from .utils import conda_channel
from .utils import requirements_txt
from .utils.base_manager import BaseManager
from .utils.base_manager import BaseManagerInfo
from .utils.base_manager import BaseRequirements
from .utils.environment import Environment
from .utils.files import temporary_files
from .utils.metadata import models

logger = logging.getLogger(__name__)

_ENVIRONMENT_FILENAME = "environment.yml"

_IMPLEMENTATIONS = ("micromamba", "mamba", "conda")


class CondaManagerInfo(BaseManagerInfo):
    name: Literal["conda"] = Field(
        default="conda",
        description="Environments described and created by `conda`.",
        examples=["conda"],
    )


class CondaRequirements(BaseRequirements):
    manager: CondaManagerInfo


class CondaManager(BaseManager):
    """Uses `conda env export` to describe an environment with an
    `environment.yml` file and `conda env update` to reproduce it. Unlike the
    python-only package managers this includes non-python dependencies.

    The command invokes conda. For example `CondaManager("micromamba")`. The
    fastest implementation available is used when no command is provided.
    """

    NAME = "conda"
    PRIORITY = 4
    REQUIREMENTS_MODEL = CondaRequirements
    COMMAND_EXAMPLE = "conda"

    def __init__(self, *command: str) -> None:
        if not command:
            command = _detect_implementation()
        super().__init__(*command)

    def version(self) -> Optional[str]:
        """Returns None when this manager is not available."""
        try:
            output = self._check_output("--version")
        except RuntimeError:
            return None
        # For example "conda 25.11.1" or "2.4.0" for mamba
        match = re.search(r"(\d+\.\d+(?:\.\d+)*)", output)
        if not match:
            return None
        return match.group(1)

    def is_active(self) -> bool:
        """Manager is explicitly active."""
        return "CONDA_PREFIX" in os.environ or _is_conda_environment(Path(sys.prefix))

    def create_environment(
        self, location: Path, python_version: Optional[str] = None
    ) -> Environment:
        """
        :raises RuntimeError: creation failed
        """
        if not python_version:
            python_version = platform.python_version()
        # 'pip' is needed for the pip section of a conda environment file
        self._check_call(
            "create",
            "--yes",
            "--quiet",
            "--prefix",
            location,
            f"python={conda_channel.python_specifier(python_version)}",
            "pip",
        )
        return self.environment(location)

    def environments_root(self) -> Path:
        """First environment directory of conda, in which `conda create --name`
        creates environments so they can be activated by name.
        """
        try:
            # 'conda config --show envs_dirs' is not supported by mamba
            info = json.loads(self._check_output("info", "--json"))
            # 'envs_dirs' for conda, 'envs directories' for mamba and micromamba
            directories = info.get("envs_dirs") or info.get("envs directories")
            return Path(directories[0])
        except (RuntimeError, ValueError, LookupError, TypeError) as ex:
            logger.warning("Cannot determine where conda creates environments (%s)", ex)
            return super().environments_root()

    def _gather_files(
        self, distributions: List[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        if not _is_conda_environment(Path(sys.prefix)):
            logger.warning(
                "The current python environment is not a conda environment. It will "
                "be reproduced from the installed python distributions."
            )
            return dict()
        output = self._check_output("env", "export", "--prefix", sys.prefix)
        return {_ENVIRONMENT_FILENAME: _without_environment_location(output)}

    def _files_from_distributions(
        self, distributions: Sequence[models.Distribution], python_version: str
    ) -> Dict[str, str]:
        requirements = requirements_txt.manifest_requirements(distributions)
        return {
            _ENVIRONMENT_FILENAME: _environment_yml(requirements, python_version),
        }

    def _install_files(
        self, files: Mapping[str, str], environment: Environment
    ) -> None:
        with temporary_files(files) as directory:
            self._check_call(
                "env",
                "update",
                "--quiet",
                "--prefix",
                environment.location,
                "--file",
                directory / _ENVIRONMENT_FILENAME,
            )

    def _add_ewoks(
        self, requirements: BaseRequirements, environment: Environment
    ) -> None:
        # The environment file pins all versions so they cannot change
        pinned = requirements_txt.manifest_requirements(requirements.distributions)
        files = {
            _ENVIRONMENT_FILENAME: _environment_yml(
                [*pinned, "ewoks"], requirements.python.version
            )
        }
        self._install_files(files, environment)


def _environment_yml(requirements: Sequence[str], python_version: str) -> str:
    """Content of a conda `environment.yml` file. Python distributions are declared
    in the `pip` section, which is how the conda environment file format expresses
    requirements that come from the python package index.
    """
    dependencies = ""
    if python_version:
        dependencies += f"  - python={conda_channel.python_specifier(python_version)}\n"
    dependencies += "  - pip\n"
    if requirements:
        dependencies += "  - pip:\n"
        dependencies += "".join(f"    - {req}\n" for req in requirements)
    return f"""channels:
  - conda-forge
dependencies:
{dependencies}"""


def _detect_implementation() -> Tuple[str, ...]:
    """The command is needed before knowing whether conda is available, so this
    does not execute anything."""
    for name in _IMPLEMENTATIONS:
        if shutil.which(name):
            return (name,)
    return (_IMPLEMENTATIONS[-1],)


def _without_environment_location(environment_yml: str) -> str:
    """Remove the name and the prefix of the exported environment: the location
    of the environment to create is provided separately.
    """
    return "".join(
        f"{line}\n"
        for line in environment_yml.splitlines()
        if not line.startswith(("name:", "prefix:"))
    )


def _is_conda_environment(prefix: Path) -> bool:
    return (prefix / "conda-meta").is_dir()
