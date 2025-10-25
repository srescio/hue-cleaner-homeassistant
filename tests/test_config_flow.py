"""Test config flow for Hue Cleaner integration."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.hue_cleaner.config_flow import HueCleanerConfigFlow
from custom_components.hue_cleaner.const import DOMAIN


class TestHueCleanerConfigFlow:
    """Test Hue Cleaner config flow."""

    async def test_user_step_invalid_ip(self, hass):
        """Test user step with invalid IP."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        
        result = await flow.async_step_user({"host": "invalid-ip"})
        
        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "invalid_ip"

    async def test_user_step_cannot_connect(self, hass):
        """Test user step with valid IP but cannot connect."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        
        with patch.object(flow, "_test_connection", return_value=False):
            result = await flow.async_step_user({"host": "192.168.1.100"})
            
            assert result["type"] == FlowResultType.FORM
            assert result["errors"]["base"] == "cannot_connect"

    async def test_user_step_success(self, hass):
        """Test user step with valid IP and connection."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        
        with patch.object(flow, "_test_connection", return_value=True):
            result = await flow.async_step_user({"host": "192.168.1.100"})
            
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "api_key"
            assert flow.hue_ip == "192.168.1.100"

    async def test_api_key_step_success(self, hass):
        """Test API key step with success."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        
        with patch.object(flow, "_fetch_api_key", return_value="test_key"):
            result = await flow.async_step_api_key({})
            
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "final_test"
            assert flow.api_key == "test_key"

    async def test_api_key_step_failure(self, hass):
        """Test API key step with failure."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        
        with patch.object(flow, "_fetch_api_key", return_value=None):
            result = await flow.async_step_api_key({})
            
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "retry_api_key"

    async def test_retry_api_key_step_back(self, hass):
        """Test retry API key step with back button."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        
        result = await flow.async_step_retry_api_key({"back": True})
        
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "api_key"

    async def test_retry_api_key_step_retry_success(self, hass):
        """Test retry API key step with retry button and success."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        
        with patch.object(flow, "_fetch_api_key", return_value="test_key"):
            result = await flow.async_step_retry_api_key({"retry": True})
            
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "final_test"
            assert flow.api_key == "test_key"

    async def test_retry_api_key_step_retry_failure(self, hass):
        """Test retry API key step with retry button and failure."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        
        with patch.object(flow, "_fetch_api_key", return_value=None):
            result = await flow.async_step_retry_api_key({"retry": True})
            
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "retry_api_key"
            assert result["errors"]["base"] == "api_key_timeout"

    async def test_final_test_success(self, hass):
        """Test final test step with success."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow.api_key = "test_key"
        
        with patch.object(flow, "_test_api_key", return_value=True):
            result = await flow.async_step_final_test({})
            
            assert result["type"] == FlowResultType.CREATE_ENTRY
            assert result["title"] == "Hue Cleaner (192.168.1.100)"
            assert result["data"]["host"] == "192.168.1.100"
            assert result["data"]["api_key"] == "test_key"

    async def test_final_test_failure(self, hass):
        """Test final test step with failure."""
        flow = HueCleanerConfigFlow()
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow.api_key = "test_key"
        
        with patch.object(flow, "_test_api_key", return_value=False):
            result = await flow.async_step_final_test({})
            
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "final_test"
            assert result["errors"]["base"] == "final_test_failed"

    def test_is_valid_ip(self):
        """Test IP validation."""
        flow = HueCleanerConfigFlow()
        
        # Valid IPs
        assert flow._is_valid_ip("192.168.1.100") is True
        assert flow._is_valid_ip("10.0.0.1") is True
        assert flow._is_valid_ip("172.16.0.1") is True
        
        # Invalid IPs
        assert flow._is_valid_ip("invalid") is False
        assert flow._is_valid_ip("192.168.1") is False
        assert flow._is_valid_ip("192.168.1.256") is False
        assert flow._is_valid_ip("") is False
