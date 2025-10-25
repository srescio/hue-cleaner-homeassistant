"""Test configuration for Hue Cleaner integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Create a mock ConfigFlow class
class MockConfigFlow:
    """Mock ConfigFlow class."""
    def __init__(self):
        """Initialize."""
        self.hass = None
        self.hue_ip = None
        self.api_key = None
        self.context = {}
        self._is_valid_ip = MagicMock()
        self._test_connection = AsyncMock()
        self._fetch_api_key = AsyncMock()
        self._test_api_key = AsyncMock()

    async def async_step_user(self, user_input=None):
        """Mock user step."""
        if not user_input:
            return {"type": "form", "step_id": "user"}

        if not self._is_valid_ip(user_input["host"]):
            return {"type": "form", "step_id": "user", "errors": {"base": "invalid_ip"}}

        if not await self._test_connection():
            return {"type": "form", "step_id": "user", "errors": {"base": "cannot_connect"}}

        self.hue_ip = user_input["host"]
        return {"type": "form", "step_id": "api_key"}

    async def async_step_api_key(self, user_input=None):
        """Mock API key step."""
        if not user_input or not user_input.get("submit"):
            return {"type": "form", "step_id": "api_key"}

        api_key = await self._fetch_api_key()
        if api_key:
            self.api_key = api_key
            return {"type": "form", "step_id": "final_test"}
        return {"type": "form", "step_id": "retry_api_key", "errors": {"base": "api_key_timeout"}}

    async def async_step_retry_api_key(self, user_input=None):
        """Mock retry API key step."""
        if not user_input:
            return {"type": "form", "step_id": "retry_api_key"}

        if user_input.get("back"):
            return {"type": "form", "step_id": "api_key"}

        if user_input.get("retry"):
            api_key = await self._fetch_api_key()
            if api_key:
                self.api_key = api_key
                return {"type": "form", "step_id": "final_test"}
            return {"type": "form", "step_id": "retry_api_key", "errors": {"base": "api_key_timeout"}}

        return {"type": "form", "step_id": "retry_api_key"}

    async def async_step_final_test(self, user_input=None):
        """Mock final test step."""
        if not user_input or not user_input.get("submit"):
            return {"type": "form", "step_id": "final_test"}

        test_result = await self._test_api_key()
        if test_result:
            return {
                "type": "create_entry",
                "title": f"Hue Cleaner ({self.hue_ip})",
                "data": {
                    "host": self.hue_ip,
                    "api_key": self.api_key
                }
            }
        return {"type": "form", "step_id": "final_test", "errors": {"base": "final_test_failed"}}

    async def async_step_issue_repair(self, user_input=None):
        """Mock issue repair step."""
        if not user_input:
            return {
                "type": "form",
                "step_id": "issue_repair",
                "description_placeholders": {
                    "issue_description": "Test issue description"
                }
            }

        if "ip_change" in self.context.get("issue_id", ""):
            if not self._is_valid_ip(user_input.get("host", "")):
                return {
                    "type": "form",
                    "step_id": "issue_repair",
                    "errors": {"base": "invalid_ip"}
                }

            if not await self._test_connection():
                return {
                    "type": "form",
                    "step_id": "issue_repair",
                    "errors": {"base": "cannot_connect"}
                }

            self.hue_ip = user_input["host"]
            return {"type": "form", "step_id": "api_key"}

        elif "api_key_expired" in self.context.get("issue_id", ""):
            test_result = await self._test_connection()
            if not test_result:
                return {
                    "type": "form",
                    "step_id": "issue_repair",
                    "errors": {"base": "cannot_connect"}
                }

            return {"type": "form", "step_id": "api_key"}

# Mock all Home Assistant modules
homeassistant_mocks = {
    'homeassistant': MagicMock(),
    'homeassistant.core': MagicMock(),
    'homeassistant.config_entries': MagicMock(ConfigFlow=MockConfigFlow),
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
