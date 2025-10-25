"""Test configuration for Hue Cleaner integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# Mock all Home Assistant modules
homeassistant_mocks = {
    'homeassistant': MagicMock(),
    'homeassistant.core': MagicMock(),
    'homeassistant.config_entries': MagicMock(),
    'homeassistant.data_entry_flow': MagicMock(),
    'homeassistant.const': MagicMock(),
    'homeassistant.helpers': MagicMock(),
    'homeassistant.helpers.aiohttp_client': MagicMock(),
    'homeassistant.helpers.update_coordinator': MagicMock(),
    'homeassistant.helpers.event': MagicMock(),
    'homeassistant.helpers.issue_registry': MagicMock(),
    'homeassistant.components': MagicMock(),
    'homeassistant.components.persistent_notification': MagicMock(),
    'homeassistant.components.sensor': MagicMock(),
    'homeassistant.helpers.entity_platform': MagicMock(),
}

patcher = patch.dict('sys.modules', homeassistant_mocks)
patcher.start()


@pytest.fixture
def mock_hass():
    """Mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    hass.states = MagicMock()
    hass.states.async_entity_ids = AsyncMock(return_value=[])
    return hass


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "host": "192.168.1.100",
        "api_key": "test_api_key"
    }
    return entry


@pytest.fixture
def mock_coordinator():
    """Mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "cleaned_count": 5,
        "last_clean": "2024-01-01T12:00:00Z",
        "areas_cleaned_this_run": 2,
        "hue_ip": "192.168.1.100",
        "status": "active",
        "mode": "event-driven"
    }
    return coordinator
