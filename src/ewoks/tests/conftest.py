from unittest.mock import MagicMock

import pytest


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
