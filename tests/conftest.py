"""Test configuration for Hue Cleaner integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


@pytest.fixture
def mock_hass():
    """Mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    return hass


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
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
        "status": "active"
    }
    return coordinator
