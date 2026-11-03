from typing import List
from unittest.mock import MagicMock

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "package_manager_install: installs package managers from the internet, "
        "only runs when selected with '-m package_manager_install'",
    )


_PACKAGE_MANAGER_INSTALL = "package_manager_install"


def pytest_collection_modifyitems(
    config: pytest.Config, items: List[pytest.Item]
) -> None:
    """Skip the tests that install package managers unless they are selected."""
    if _PACKAGE_MANAGER_INSTALL in config.getoption("markexpr", ""):
        return
    skip = pytest.mark.skip(
        reason=f"installs package managers: select with '-m {_PACKAGE_MANAGER_INSTALL}'"
    )
    for item in items:
        if _PACKAGE_MANAGER_INSTALL in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def mock_icat_client(monkeypatch):
    mock_defaults = MagicMock()
    mock_defaults.METADATA_BROKERS = ["mock://broker"]

    # Create a mock for IcatClient
    mock_client = MagicMock()
    mock_client_instance = mock_client.return_value
    mock_client_instance.store_processed_data.return_value = None

    # Patch the imports in your module (replace 'your_module' with actual module name)
    monkeypatch.setattr("ewoks.bindings.icat_defaults", mock_defaults)
    monkeypatch.setattr("ewoks.bindings.IcatClient", mock_client)

    return mock_client
