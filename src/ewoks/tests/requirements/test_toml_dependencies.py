"""Tests of the dependencies of a TOML manifest."""

from ..._requirements.utils import toml_dependencies
from .utils import DISTRIBUTIONS
from .utils import REQUIREMENTS


def test_dependency_lines():
    """Dependencies of a TOML manifest are not PEP 508 requirements."""
    requirements = [
        *REQUIREMENTS,
        "mypackag1",
        "mypackage2 @ git+https://host/group/repo.git@123",
        "mypackage3 @ https://host/mypackage3-1.0-py3-none-any.whl",
    ]

    assert toml_dependencies.dependency_lines(requirements) == [
        *(f'"{dist.name}" = "=={dist.version}"' for dist in DISTRIBUTIONS),
        '"mypackag1" = "*"',
        '"mypackage2" = { git = "https://host/group/repo.git", rev = "123" }',
        '"mypackage3" = { url = "https://host/mypackage3-1.0-py3-none-any.whl" }',
    ]


def test_invalid_dependency(caplog):
    assert toml_dependencies.dependency_lines(["git+https://host/repo"]) == []
    assert "Skip invalid requirement" in caplog.text
