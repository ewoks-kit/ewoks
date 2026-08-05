import shutil
from typing import Iterator

import pytest

from .managers import Environment
from .managers import ManagerCase


@pytest.fixture
def manager_case(request) -> ManagerCase:
    """Package manager under test, selected with `parametrize_managers` or
    `parametrize_freeze_managers`.
    """
    case: ManagerCase = request.param
    if case.manager().version() is None:
        pytest.skip(f"{case.NAME} is not installed")
    return case


@pytest.fixture
def environment(manager_case, tmp_path) -> Iterator[Environment]:
    """Empty python environment created by the package manager under test."""
    path = tmp_path / "environment"
    try:
        yield manager_case.create_environment(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)
