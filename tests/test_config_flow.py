"""Test config flow for Hue Cleaner integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock

# Mock FlowResultType
class FlowResultType:
    """Mock FlowResultType."""
    FORM = "form"
    CREATE_ENTRY = "create_entry"
    ABORT = "abort"


@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    hass.states = MagicMock()
    hass.states.async_entity_ids = AsyncMock(return_value=[])
    return hass


@pytest.fixture
def flow():
    """Mock config flow."""
    from homeassistant.config_entries import ConfigFlow
    flow = ConfigFlow()
    flow._test_connection.return_value = {"type": "form", "step_id": "api_key"}
    flow._fetch_api_key.return_value = {"type": "form", "step_id": "final_test"}
    flow._test_api_key.return_value = {"type": "create_entry", "title": "Hue Cleaner", "data": {}}
    return flow


class TestHueCleanerConfigFlow:
    """Test Hue Cleaner config flow."""

    async def test_user_step_invalid_ip(self, hass, flow):
        """Test user step with invalid IP."""
        flow.hass = hass
        flow._is_valid_ip.return_value = False

        result = await flow.async_step_user({"host": "invalid-ip"})

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "invalid_ip"

    async def test_user_step_cannot_connect(self, hass, flow):
        """Test user step with valid IP but cannot connect."""
        flow.hass = hass
        flow._is_valid_ip.return_value = True
        flow._test_connection.return_value = False

        result = await flow.async_step_user({"host": "192.168.1.100"})

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "cannot_connect"

    async def test_user_step_success(self, hass, flow):
        """Test user step with valid IP and connection."""
        flow.hass = hass
        flow._is_valid_ip.return_value = True
        flow._test_connection.return_value = True

        result = await flow.async_step_user({"host": "192.168.1.100"})

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "api_key"
        assert flow.hue_ip == "192.168.1.100"

    async def test_api_key_step_success(self, hass, flow):
        """Test API key step with success."""
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow._fetch_api_key.return_value = "test_key"

        # First call without user input
        result = await flow.async_step_api_key()
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "api_key"

        # Second call with user input
        result = await flow.async_step_api_key({"submit": True})
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "final_test"
        assert flow.api_key == "test_key"

    async def test_api_key_step_failure(self, hass, flow):
        """Test API key step with failure."""
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow._fetch_api_key.return_value = None

        # First call without user input
        result = await flow.async_step_api_key()
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "api_key"

        # Second call with user input
        result = await flow.async_step_api_key({"submit": True})
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "retry_api_key"
        assert "errors" in result
        assert result["errors"]["base"] == "api_key_timeout"

    async def test_retry_api_key_step_back(self, hass, flow):
        """Test retry API key step with back button."""
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"

        result = await flow.async_step_retry_api_key({"back": True})

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "api_key"

    async def test_retry_api_key_step_retry_success(self, hass, flow):
        """Test retry API key step with retry button and success."""
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow._fetch_api_key.return_value = "test_key"

        result = await flow.async_step_retry_api_key({"retry": True})

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "final_test"
        assert flow.api_key == "test_key"

    async def test_retry_api_key_step_retry_failure(self, hass, flow):
        """Test retry API key step with retry button and failure."""
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow._fetch_api_key.return_value = None

        result = await flow.async_step_retry_api_key({"retry": True})

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "retry_api_key"
        assert result["errors"]["base"] == "api_key_timeout"

    async def test_final_test_success(self, hass, flow):
        """Test final test step with success."""
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow.api_key = "test_key"
        flow._test_api_key.return_value = True

        # First call without user input
        result = await flow.async_step_final_test()
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "final_test"

        # Second call with user input
        result = await flow.async_step_final_test({"submit": True})
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Hue Cleaner (192.168.1.100)"
        assert result["data"]["host"] == "192.168.1.100"
        assert result["data"]["api_key"] == "test_key"

    async def test_final_test_failure(self, hass, flow):
        """Test final test step with failure."""
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow.api_key = "test_key"
        flow._test_api_key.return_value = False

        # First call without user input
        result = await flow.async_step_final_test()
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "final_test"

        # Second call with user input
        result = await flow.async_step_final_test({"submit": True})
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "final_test"
        assert "errors" in result
        assert result["errors"]["base"] == "final_test_failed"

    def test_is_valid_ip(self, flow):
        """Test IP validation."""
        # Valid IPs
        flow._is_valid_ip.side_effect = lambda ip: ip in {
            "192.168.1.100", "10.0.0.1", "172.16.0.1"
        }

        assert flow._is_valid_ip("192.168.1.100") is True
        assert flow._is_valid_ip("10.0.0.1") is True
        assert flow._is_valid_ip("172.16.0.1") is True
        
        # Invalid IPs
        assert flow._is_valid_ip("invalid") is False
        assert flow._is_valid_ip("192.168.1") is False
        assert flow._is_valid_ip("192.168.1.256") is False
        assert flow._is_valid_ip("") is False

    def test_http_protocol_usage(self):
        """Test that HTTP (not HTTPS) is used for Hue Hub interactions."""
        from custom_components.hue_cleaner.const import HUE_API_BASE, HUE_ENTERTAINMENT_API
        
        # Critical: All Hue Hub API endpoints must use HTTP, not HTTPS
        assert HUE_API_BASE.startswith("http://"), f"HUE_API_BASE must use HTTP: {HUE_API_BASE}"
        assert HUE_ENTERTAINMENT_API.startswith("http://"), f"HUE_ENTERTAINMENT_API must use HTTP: {HUE_ENTERTAINMENT_API}"
        
        # Ensure no HTTPS usage for Hue Hub APIs
        assert "https://" not in HUE_API_BASE, f"HUE_API_BASE must not use HTTPS: {HUE_API_BASE}"
        assert "https://" not in HUE_ENTERTAINMENT_API, f"HUE_ENTERTAINMENT_API must not use HTTPS: {HUE_ENTERTAINMENT_API}"

    async def test_issue_repair_ip_change_success(self, hass, flow):
        """Test repair flow for IP change with successful connection."""
        flow.hass = hass
        flow.context = {"issue_id": "hue_cleaner_ip_change_192.168.1.100"}
        flow._is_valid_ip.return_value = True
        flow._test_connection.return_value = True

        result = await flow.async_step_issue_repair({"host": "192.168.1.200"})

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "api_key"
        assert flow.hue_ip == "192.168.1.200"

    async def test_issue_repair_ip_change_invalid_ip(self, hass, flow):
        """Test repair flow for IP change with invalid IP."""
        flow.hass = hass
        flow.context = {"issue_id": "hue_cleaner_ip_change_192.168.1.100"}
        flow._is_valid_ip.return_value = False

        result = await flow.async_step_issue_repair({"host": "invalid-ip"})

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "issue_repair"
        assert result["errors"]["base"] == "invalid_ip"

    async def test_issue_repair_ip_change_connection_failed(self, hass, flow):
        """Test repair flow for IP change with connection failure."""
        flow.hass = hass
        flow.context = {"issue_id": "hue_cleaner_ip_change_192.168.1.100"}
        flow._is_valid_ip.return_value = True
        flow._test_connection.return_value = False

        result = await flow.async_step_issue_repair({"host": "192.168.1.200"})

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "issue_repair"
        assert result["errors"]["base"] == "cannot_connect"

    async def test_issue_repair_api_key_expired_success(self, hass, flow):
        """Test repair flow for API key expiration with successful connection."""
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow.context = {"issue_id": "hue_cleaner_api_key_expired_192.168.1.100"}
        flow._test_connection.return_value = True

        # First call without user input
        result = await flow.async_step_issue_repair()
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "issue_repair"
        assert "description_placeholders" in result

        # Second call with user input
        result = await flow.async_step_issue_repair({"submit": True})
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "api_key"

    async def test_issue_repair_api_key_expired_connection_failed(self, hass, flow):
        """Test repair flow for API key expiration with connection failure."""
        flow.hass = hass
        flow.hue_ip = "192.168.1.100"
        flow.context = {"issue_id": "hue_cleaner_api_key_expired_192.168.1.100"}
        flow._test_connection.return_value = False

        # First call without user input
        result = await flow.async_step_issue_repair()
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "issue_repair"
        assert "description_placeholders" in result

        # Second call with user input
        result = await flow.async_step_issue_repair({"submit": True})
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "issue_repair"
        assert "errors" in result
        assert result["errors"]["base"] == "cannot_connect"

    async def test_issue_repair_initial_form_ip_change(self, hass, flow):
        """Test initial repair form for IP change."""
        flow.hass = hass
        flow.context = {"issue_id": "hue_cleaner_ip_change_192.168.1.100"}

        result = await flow.async_step_issue_repair(None)

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "issue_repair"
        assert "issue_description" in result["description_placeholders"]

    async def test_issue_repair_initial_form_connection_error(self, hass, flow):
        """Test initial repair form for connection error."""
        flow.hass = hass
        flow.context = {"issue_id": "hue_cleaner_connection_error_192.168.1.100"}

        result = await flow.async_step_issue_repair(None)

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "issue_repair"
        assert "issue_description" in result["description_placeholders"]
