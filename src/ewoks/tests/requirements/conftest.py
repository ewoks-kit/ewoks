import shutil
from pathlib import Path
from typing import Dict
from typing import Iterator

import pytest

from ..._requirements.utils.base_manager import BaseManager
from ..._requirements.utils.environment import Environment
from .managers import FAST_MANAGER_CASES
from .managers import MANAGER_CASES
from .managers import ManagerCase

_IDS = [case.NAME for case in MANAGER_CASES]
_FAST_IDS = [case.NAME for case in FAST_MANAGER_CASES]


@pytest.fixture(scope="package", autouse=True)
def isolated_home(tmp_path_factory) -> Iterator[Path]:
    """Home directory of the package managers, in which they cache their downloads
    and store their configuration. It is inside the pytest temporary directory so a
    test run does not write anywhere else. The downside is that the caches are
    empty at the start of every test run.
    """
    home = tmp_path_factory.mktemp("home")
    with pytest.MonkeyPatch.context() as monkeypatch:
        for name, path in _home_variables(home).items():
            monkeypatch.setenv(name, str(path))
        yield home
    # The caches are not reused by the next test run and fill up the disk
    shutil.rmtree(home, ignore_errors=True)


def _home_variables(home: Path) -> Dict[str, Path]:
    """Environment variables that move everything a package manager writes
    outside a python environment to this home directory.
    """
    condarc = home / ".condarc"
    with open(condarc, "w", encoding="utf-8") as fh:
        fh.write("channels:\n  - conda-forge\n")
    return {
        # Home directory on Linux, macOS and Windows
        "HOME": home,
        "USERPROFILE": home,
        "APPDATA": home,
        "LOCALAPPDATA": home,
        "XDG_CACHE_HOME": home / ".cache",
        "XDG_CONFIG_HOME": home / ".config",
        "XDG_DATA_HOME": home / ".local" / "share",
        # Conda downloads packages next to its own installation instead
        "CONDA_PKGS_DIRS": home / "conda" / "pkgs",
        # Directories in which package managers create named environments
        "CONDA_ENVS_DIRS": home / "conda" / "envs",
        "POETRY_VIRTUALENVS_PATH": home / "poetry" / "virtualenvs",
        # Channels are no longer provided by the home directory of the user
        "CONDARC": condarc,
    }


@pytest.fixture
def env_root(tmp_path) -> Iterator[Path]:
    """Root directory of the environments created by a test."""
    yield tmp_path
    # Environments are large and there are many tests
    shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture(params=MANAGER_CASES, ids=_IDS)
def manager_case(request) -> ManagerCase:
    """Repeats the test for every package manager."""
    return _manager_case(request)


@pytest.fixture
def manager(manager_case) -> BaseManager:
    """Package manager under test."""
    return manager_case.manager()


@pytest.fixture
def environment(manager_case, tmp_path) -> Iterator[Environment]:
    """Empty python environment created by the package manager under test."""
    yield from _environment(manager_case, tmp_path)


@pytest.fixture(params=FAST_MANAGER_CASES, ids=_FAST_IDS)
def fast_manager_case(request) -> ManagerCase:
    """Repeats the test for every package manager that is fast. Use this when the
    package manager is not the subject of the test."""
    return _manager_case(request)


@pytest.fixture
def fast_manager(fast_manager_case) -> BaseManager:
    """Package manager under test, one that is fast."""
    return fast_manager_case.manager()


@pytest.fixture
def fast_environment(fast_manager_case, tmp_path) -> Iterator[Environment]:
    """Empty python environment created by a package manager that is fast."""
    yield from _environment(fast_manager_case, tmp_path)


@pytest.fixture(params=FAST_MANAGER_CASES, ids=_FAST_IDS)
def source_manager_case(request) -> ManagerCase:
    """Repeats the test for every package manager that could have generated the
    requirements to be installed."""
    return _manager_case(request)


def _manager_case(request) -> ManagerCase:
    case: ManagerCase = request.param
    if case.manager().version() is None:
        pytest.skip(f"{case.NAME} is not installed")
    return case


def _environment(case: ManagerCase, tmp_path) -> Iterator[Environment]:
    location = tmp_path / "environment"
    yield case.manager().create_environment(location)
    # Environments are large and there are many tests
    shutil.rmtree(location, ignore_errors=True)
