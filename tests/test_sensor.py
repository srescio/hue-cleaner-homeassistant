"""Test sensor for Hue Cleaner integration."""
import pytest
from unittest.mock import MagicMock, patch

# Create base classes with the same metaclass
class MockEntity(type):
    """Mock entity metaclass."""
    def __new__(cls, name, bases, attrs):
        return super().__new__(cls, name, bases, attrs)

class MockSensorEntity(metaclass=MockEntity):
    """Mock sensor entity."""
    def __init__(self, *args, **kwargs):
        pass

class MockCoordinatorEntity(metaclass=MockEntity):
    """Mock coordinator entity."""
    def __init__(self, coordinator):
        pass

# Mock Home Assistant modules before any imports
mock_modules = {
    'homeassistant': MagicMock(),
    'homeassistant.core': MagicMock(),
    'homeassistant.config_entries': MagicMock(),
    'homeassistant.data_entry_flow': MagicMock(),
    'homeassistant.const': MagicMock(),
    'homeassistant.helpers': MagicMock(),
    'homeassistant.helpers.aiohttp_client': MagicMock(),
    'homeassistant.helpers.update_coordinator': MagicMock(CoordinatorEntity=MockCoordinatorEntity),
    'homeassistant.helpers.event': MagicMock(),
    'homeassistant.helpers.issue_registry': MagicMock(),
    'homeassistant.components': MagicMock(),
    'homeassistant.components.persistent_notification': MagicMock(),
    'homeassistant.components.sensor': MagicMock(SensorEntity=MockSensorEntity),
    'homeassistant.helpers.entity_platform': MagicMock(),
    'aiohttp': MagicMock(),
    'voluptuous': MagicMock(),
}

# Mock the modules
with patch.dict('sys.modules', mock_modules):
    from custom_components.hue_cleaner.sensor import HueCleanerSensor


class TestHueCleanerSensor:
    """Test Hue Cleaner sensor."""

    @pytest.fixture
    def sensor(self, mock_coordinator):
        """Create sensor instance."""
        return HueCleanerSensor(mock_coordinator)

    def test_sensor_properties(self, sensor):
        """Test sensor properties."""
        assert sensor.name == "Hue Cleaner"
        assert sensor.unique_id == "hue_cleaner_status"

    def test_native_value(self, sensor):
        """Test sensor native value."""
        assert sensor.native_value == "active"

    def test_extra_state_attributes(self, sensor):
        """Test sensor extra state attributes."""
        attrs = sensor.extra_state_attributes
        
        assert attrs["cleaned_count"] == 5
        assert attrs["last_clean"] == "2024-01-01T12:00:00Z"
        assert attrs["areas_cleaned_this_run"] == 2
        assert attrs["hue_ip"] == "192.168.1.100"
        assert attrs["mode"] == "event-driven"

    def test_extra_state_attributes_with_error_mode(self, mock_coordinator):
        """Test sensor extra state attributes with error mode."""
        mock_coordinator.data["status"] = "error"
        mock_coordinator.data["mode"] = "polling"
        
        sensor = HueCleanerSensor(mock_coordinator)
        attrs = sensor.extra_state_attributes
        
        assert attrs["mode"] == "polling"
        assert sensor.native_value == "error"

    def test_extra_state_attributes_missing_data(self, mock_coordinator):
        """Test sensor extra state attributes with missing data."""
        mock_coordinator.data = {}
        
        sensor = HueCleanerSensor(mock_coordinator)
        attrs = sensor.extra_state_attributes
        
        assert attrs["cleaned_count"] == 0
        assert attrs["areas_cleaned_this_run"] == 0
        assert attrs["hue_ip"] is None
        assert attrs["mode"] == "unknown"
        assert sensor.native_value == "unknown"
