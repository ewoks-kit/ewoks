import importlib.metadata
import os
import subprocess
import sys
from functools import lru_cache
from typing import Dict
from typing import NamedTuple
from typing import Optional
from typing import Type

from ..pip import PipManager
from .base import BaseManager

# from ..conda import CondaManager
# from ..pipenv import PipenvManager
# from ..pixi import PixiManager
# from ..poetry import PoetryManager
# from ..uv import UvManager


class ManagerInfo(NamedTuple):
    manager_type: Type[BaseManager]
    version: Optional[str]
    is_active: bool
    priority: int


@lru_cache
def get_supported_managers() -> Dict[str, ManagerInfo]:
    return dict(
        pip=ManagerInfo(
            manager_type=PipManager,
            version=_get_pip_version(),
            is_active=False,
            priority=0,
        ),
        # uv=ManagerInfo(
        #     manager_type=UvManager,
        #     version=_get_uv_version(),
        #     is_active=False,
        #     priority=1,
        # ),
        # poetry=ManagerInfo(
        #     manager_type=PoetryManager,
        #     version=_get_poetry_version(),
        #     is_active=_is_poetry_active(),
        #     priority=2,
        # ),
        # pipenv=ManagerInfo(
        #     manager_type=PipenvManager,
        #     version=_get_pipenv_version(),
        #     is_active=_is_pipenv_active(),
        #     priority=3,
        # ),
        # conda=ManagerInfo(
        #     manager_type=CondaManager,
        #     version=_get_conda_version(),
        #     is_active=_is_conda_active(),
        #     priority=4,
        # ),
        # pixi=ManagerInfo(
        #     manager_type=PixiManager,
        #     version=_get_pixi_version(),
        #     is_active=_is_pixi_active(),
        #     priority=5,
        # ),
    )


def _get_pip_version() -> Optional[str]:
    try:
        return importlib.metadata.version("pip")
    except importlib.metadata.PackageNotFoundError:
        return None


def _get_poetry_version() -> Optional[str]:
    try:
        return importlib.metadata.version("poetry")
    except importlib.metadata.PackageNotFoundError:
        return None


def _get_pipenv_version() -> Optional[str]:
    try:
        return importlib.metadata.version("pipenv")
    except importlib.metadata.PackageNotFoundError:
        return None


def _get_conda_version() -> Optional[str]:
    try:
        output = subprocess.check_output(["conda", "--version"], text=True)
        return output.strip().split(" ")[-1]
    except Exception:
        return None


def _get_pixi_version() -> Optional[str]:
    try:
        output = subprocess.check_output(["pixi", "--version"], text=True)
        return output.strip().split(" ")[-1]
    except Exception:
        return None


def _get_uv_version() -> Optional[str]:
    try:
        output = subprocess.check_output(["uv", "--version"], text=True)
        return output.strip().split(" ")[-1]
    except Exception:
        return None


def _is_conda_active() -> bool:
    return "CONDA_PREFIX" in os.environ or os.path.exists(
        os.path.join(sys.prefix, "conda-meta")
    )


def _is_pixi_active() -> bool:
    return "PIXI_PROJECT_ROOT" in os.environ


def _is_poetry_active() -> bool:
    return "POETRY_ACTIVE" in os.environ


def _is_pipenv_active() -> bool:
    return "PIPENV_ACTIVE" in os.environ


def _in_virtual_environment() -> bool:
    return sys.prefix != sys.base_prefix
