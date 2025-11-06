import subprocess
import sys
from functools import lru_cache
from typing import Dict
from typing import Tuple


def get_manager_command(manager_name: str) -> Tuple[str, ...]:
    return manager_commands()[manager_name]


@lru_cache
def manager_commands() -> Dict[str, Tuple[str, ...]]:
    return dict(
        pip=(sys.executable, "-m", "pip"),
        poetry=(sys.executable, "-m", "poetry"),
        pipenv=(sys.executable, "-m", "pipenv"),
        conda=_get_conda_command(),
        pixi=("pixi",),
        uv=("uv",),
    )


def _get_conda_command() -> Tuple[str, ...]:
    try:
        _ = subprocess.check_output(["mamba", "--version"], text=True)
        return ("mamba",)
    except Exception:
        pass
    try:
        _ = subprocess.check_output(["micromamba", "--version"], text=True)
        return ("micromamba",)
    except Exception:
        pass
    return ("conda",)
