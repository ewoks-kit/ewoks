"""Tests that apply to all package managers."""

import pytest

from ..._requirements.utils.detect import get_manager
from .managers import parametrize_managers

pytestmark = parametrize_managers


def test_available(manager_case):
    version = manager_case.manager().version()
    assert version
    assert version[0].isdigit()


def test_not_available(manager_case, monkeypatch):
    monkeypatch.setattr(manager_case.MANAGER_CLS, "version", lambda self: None)
    with pytest.raises(ValueError, match="not available"):
        get_manager(manager_name=manager_case.NAME)


def test_select_manager(manager_case, environment):
    manager = get_manager(
        manager_name=manager_case.NAME,
        manager_command=manager_case.command(environment),
    )
    assert isinstance(manager, manager_case.MANAGER_CLS)


def test_is_active(manager_case):
    assert isinstance(manager_case.manager().is_active(), bool)


def test_gather_requirements(manager_case, environment):
    requirements = manager_case.manager(environment).gather_requirements()

    assert isinstance(requirements, manager_case.MANAGER_CLS.REQUIREMENTS_MODEL)
    assert requirements.manager.name == manager_case.NAME
    assert requirements.manager.version
    assert requirements.python.version
    assert requirements.distributions
