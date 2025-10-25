"""Test sensor for Hue Cleaner integration."""
import pytest
from unittest.mock import MagicMock

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
