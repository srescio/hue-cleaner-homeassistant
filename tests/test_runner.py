#!/usr/bin/env python3
"""Test runner that mocks Home Assistant and runs tests."""

import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    'homeassistant.helpers.update_coordinator': MagicMock(),
    'homeassistant.helpers.event': MagicMock(),
    'homeassistant.helpers.issue_registry': MagicMock(),
    'homeassistant.components': MagicMock(),
    'homeassistant.components.persistent_notification': MagicMock(),
    'homeassistant.components.sensor': MagicMock(SensorEntity=MockSensorEntity),
    'homeassistant.helpers.entity_platform': MagicMock(),
    'homeassistant.helpers.update_coordinator': MagicMock(CoordinatorEntity=MockCoordinatorEntity),
    'aiohttp': MagicMock(),
    'voluptuous': MagicMock(),
}

# Mock the modules
with patch.dict('sys.modules', mock_modules):
    # Now we can import and test
    from custom_components.hue_cleaner.coordinator import HueCleanerCoordinator
    from custom_components.hue_cleaner.config_flow import HueCleanerConfigFlow
    from custom_components.hue_cleaner.sensor import HueCleanerSensor
    from custom_components.hue_cleaner.const import DOMAIN, HUE_API_BASE, HUE_ENTERTAINMENT_API

def test_http_protocol_usage():
    """Test that HTTP (not HTTPS) is used for Hue Hub interactions."""
    # Critical: All Hue Hub API endpoints must use HTTP, not HTTPS
    assert HUE_API_BASE.startswith("http://"), f"HUE_API_BASE must use HTTP: {HUE_API_BASE}"
    assert HUE_ENTERTAINMENT_API.startswith("http://"), f"HUE_ENTERTAINMENT_API must use HTTP: {HUE_ENTERTAINMENT_API}"
    
    # Ensure no HTTPS usage for Hue Hub APIs
    assert "https://" not in HUE_API_BASE, f"HUE_API_BASE must not use HTTPS: {HUE_API_BASE}"
    assert "https://" not in HUE_ENTERTAINMENT_API, f"HUE_ENTERTAINMENT_API must not use HTTPS: {HUE_ENTERTAINMENT_API}"
    
    print("✅ HTTP protocol usage test passed")

def test_coordinator_error_handling():
    """Test coordinator error handling methods exist."""
    # Create a mock hass
    mock_hass = MagicMock()
    mock_hass.data = {}
    mock_hass.states = MagicMock()
    mock_hass.states.async_entity_ids = MagicMock(return_value=[])
    
    # Create coordinator
    coordinator = HueCleanerCoordinator(mock_hass, "192.168.1.100", "test_key")
    
    # Test that error handling methods exist
    assert hasattr(coordinator, '_handle_connection_error')
    assert hasattr(coordinator, '_create_error_notification')
    assert hasattr(coordinator, '_create_repair_issue')
    assert hasattr(coordinator, '_clear_repair_issues')
    
    print("✅ Coordinator error handling methods exist")

def test_config_flow_repair_step():
    """Test config flow has repair step."""
    flow = HueCleanerConfigFlow()
    
    # Test that repair step exists
    assert hasattr(flow, 'async_step_issue_repair')
    
    print("✅ Config flow repair step exists")

def test_sensor_error_attributes():
    """Test sensor handles error attributes."""
    # Create mock coordinator
    mock_coordinator = MagicMock()
    mock_coordinator.data = {
        "status": "error",
        "mode": "polling",
        "cleaned_count": 0,
        "areas_cleaned_this_run": 0,
        "hue_ip": None,
    }
    
    # Create sensor
    sensor = HueCleanerSensor(mock_coordinator)
    
    # Test error state
    assert sensor.native_value == "error"
    attrs = sensor.extra_state_attributes
    assert attrs["mode"] == "polling"
    assert attrs["cleaned_count"] == 0
    
    print("✅ Sensor error attributes test passed")

def main():
    """Run all tests."""
    print("🧪 Running Hue Cleaner error handling tests...\n")
    
    tests = [
        ("HTTP Protocol Usage", test_http_protocol_usage),
        ("Coordinator Error Handling", test_coordinator_error_handling),
        ("Config Flow Repair Step", test_config_flow_repair_step),
        ("Sensor Error Attributes", test_sensor_error_attributes),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"📋 {test_name}:")
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            failed += 1
        print()
    
    print(f"🎯 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All error handling tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
