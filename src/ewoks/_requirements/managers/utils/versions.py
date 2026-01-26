import importlib.metadata
import subprocess
from functools import lru_cache
from typing import Dict
from typing import Optional


def get_manager_version(manager_name: str) -> str:
    version = manager_versions()[manager_name]
    if version is None:
        raise RuntimeError(f"{manager_name!r} is not installed")
    return version


@lru_cache
def manager_versions() -> Dict[str, Optional[str]]:
    return dict(
        pip=_get_pip_version(),
        poetry=_get_poetry_version(),
        pipenv=_get_pipenv_version(),
        conda=_get_conda_version(),
        pixi=_get_pixi_version(),
        uv=_get_uv_version(),
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
