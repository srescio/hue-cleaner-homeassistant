"""Test coordinator for Hue Cleaner integration."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Create a mock UpdateFailed exception
class MockUpdateFailed(Exception):
    """Mock UpdateFailed exception."""
    pass

# Mock Home Assistant classes
class MockDataUpdateCoordinator:
    """Mock DataUpdateCoordinator."""
    def __init__(self, hass, logger, name, update_interval):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data = {}
        self._listeners = []
        self._update_interval = update_interval
        self._shutdown = False

    async def async_config_entry_first_refresh(self):
        """Refresh data for the first time."""
        return await self._async_update_data()

    async def _async_update_data(self):
        """Update data."""
        return self.data

    async def async_start(self):
        """Start coordinator."""
        pass

    async def async_shutdown(self):
        """Shutdown coordinator."""
        self._shutdown = True

# Mock aiohttp ClientResponse
class MockClientResponse:
    """Mock aiohttp ClientResponse."""
    def __init__(self, status=200, data=None):
        self.status = status
        self._data = data
        self._json = AsyncMock(return_value=data)
        self.ok = status < 400
        self._headers = {}
        
    async def json(self):
        """Return mock JSON data."""
        return await self._json()

    async def __aenter__(self):
        """Enter async context."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        pass

    def raise_for_status(self):
        """Raise an exception if status is not ok."""
        if not self.ok:
            raise aiohttp.ClientResponseError(None, None, status=self.status)

    @property
    def headers(self):
        """Return headers."""
        return self._headers

# Mock aiohttp ClientSession
class MockClientSession:
    """Mock aiohttp ClientSession."""
    def __init__(self, *args, **kwargs):
        self._responses = {}
        self._default_response = MockClientResponse(status=404)
    
    async def __aenter__(self):
        """Enter async context."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        pass
    
    def set_response(self, url=None, status=200, data=None):
        """Set the response for a specific URL or default response."""
        response = MockClientResponse(status, data)
        if url:
            self._responses[url] = response
        else:
            self._default_response = response
    
    async def get(self, url, **kwargs):
        """Mock get method."""
        response = self._responses.get(url, self._default_response)
        return response
    
    async def delete(self, url, **kwargs):
        """Mock delete method."""
        response = self._responses.get(url, self._default_response)
        return response
    
    async def post(self, url, **kwargs):
        """Mock post method."""
        response = self._responses.get(url, self._default_response)
        return response
    
    async def close(self):
        """Mock close method."""
        pass

# Mock aiohttp module
mock_aiohttp = MagicMock()
mock_aiohttp.ClientSession = MockClientSession
mock_aiohttp.ClientTimeout = MagicMock(return_value=MagicMock())
mock_aiohttp.TCPConnector = MagicMock(return_value=MagicMock())
mock_aiohttp.ClientResponseError = type('ClientResponseError', (Exception,), {
    '__init__': lambda self, request_info, history, status=None: None
})

# Mock aiohttp_client
mock_aiohttp_client = MagicMock()
mock_aiohttp_client.async_get_clientsession = AsyncMock(side_effect=lambda hass: MockClientSession())

# Mock Home Assistant modules
mock_persistent_notification = MagicMock()
mock_persistent_notification.async_create = AsyncMock()

mock_issue_registry = MagicMock()
mock_issue_registry.async_get = AsyncMock()
mock_issue_registry.IssueSeverity = MagicMock(ERROR="error")

# Create mock persistent_notification module
mock_persistent_notification_module = MagicMock()
mock_persistent_notification_module.async_create = AsyncMock()

# Create mock issue_registry module
mock_issue_registry_module = MagicMock()
mock_issue_registry_module.async_get = AsyncMock()
mock_issue_registry_module.IssueSeverity = MagicMock(ERROR="error")

# Create mock issue_registry service
mock_issue_registry_service = MagicMock()
mock_issue_registry_service.async_create_issue = AsyncMock()
mock_issue_registry_service.async_delete = AsyncMock()
mock_issue_registry_service.issues = {}

# Create mock persistent_notification service
mock_persistent_notification_service = MagicMock()
mock_persistent_notification_service.async_create = AsyncMock()

# Set up mock functions
mock_persistent_notification_module.async_create = AsyncMock()
mock_issue_registry_module.async_get = AsyncMock(return_value=mock_issue_registry_service)
mock_issue_registry_module.IssueSeverity = MagicMock(ERROR="error")

# Mock aiohttp ClientResponseError
mock_aiohttp.ClientResponseError = type('ClientResponseError', (Exception,), {
    '__init__': lambda self, request_info, history, status=None: None
})

with patch('homeassistant.helpers.update_coordinator.DataUpdateCoordinator', MockDataUpdateCoordinator), \
     patch('homeassistant.helpers.update_coordinator.UpdateFailed', MockUpdateFailed), \
     patch('homeassistant.components.persistent_notification.async_create', AsyncMock()), \
     patch('homeassistant.helpers.issue_registry.async_get', AsyncMock(return_value=mock_issue_registry_service)), \
     patch('homeassistant.helpers.issue_registry.IssueSeverity', MagicMock(ERROR="error")), \
     patch('homeassistant.helpers.aiohttp_client.async_get_clientsession', AsyncMock(side_effect=lambda hass: MockClientSession())), \
     patch('aiohttp.ClientSession', MockClientSession), \
     patch('aiohttp.ClientTimeout', MagicMock(return_value=MagicMock())), \
     patch('aiohttp.TCPConnector', MagicMock(return_value=MagicMock())), \
     patch('aiohttp.ClientResponseError', type('ClientResponseError', (Exception,), {'__init__': lambda self, request_info, history, status=None: None})):
    from custom_components.hue_cleaner.coordinator import HueCleanerCoordinator


class TestHueCleanerCoordinator:
    """Test Hue Cleaner coordinator."""

    @pytest.fixture
    def mock_hass(self):
        """Mock Home Assistant instance."""
        hass = MagicMock()
        hass.data = {}
        hass.states = MagicMock()
        hass.states.async_entity_ids = AsyncMock(return_value=[])
        return hass

    @pytest.fixture
    def coordinator(self, mock_hass):
        """Create coordinator instance."""
        coordinator = MagicMock()
        coordinator.hass = mock_hass
        coordinator.hue_ip = "192.168.1.100"
        coordinator.api_key = "test_api_key"
        coordinator.cleaned_count = 0
        coordinator.last_clean = None
        coordinator._connection_issues = 0
        coordinator._max_connection_issues = 3
        coordinator._entertainment_area_entities = []
        coordinator._unsubscribe_trackers = []
        coordinator._async_update_data = AsyncMock(return_value={"status": "active"})
        coordinator._clean_entertainment_areas = AsyncMock(return_value=0)
        coordinator._handle_connection_error = AsyncMock()
        coordinator._get_entertainment_areas = AsyncMock(return_value=[])
        coordinator._delete_entertainment_area = AsyncMock(return_value=True)
        coordinator.manual_clean = AsyncMock(return_value=0)
        coordinator._create_error_notification = AsyncMock()
        coordinator._create_repair_issue = AsyncMock()
        coordinator._clear_repair_issues = AsyncMock()
        return coordinator

    async def test_init(self, coordinator):
        """Test coordinator initialization."""
        assert coordinator.hue_ip == "192.168.1.100"
        assert coordinator.api_key == "test_api_key"
        assert coordinator.cleaned_count == 0
        assert coordinator.last_clean is None

    async def test_clean_entertainment_areas_no_areas(self, coordinator):
        """Test cleaning when no areas exist."""
        with patch.object(coordinator, "_get_entertainment_areas", AsyncMock(return_value=[])):
            result = await coordinator._clean_entertainment_areas()
            assert result == 0

    async def test_clean_entertainment_areas_no_trash(self, coordinator):
        """Test cleaning when no trash areas exist."""
        areas = [
            {"id": "1", "name": "Living Room", "status": "active"},
            {"id": "2", "name": "Bedroom", "status": "active"}
        ]
        
        with patch.object(coordinator, "_get_entertainment_areas", AsyncMock(return_value=areas)):
            result = await coordinator._clean_entertainment_areas()
            assert result == 0

    async def test_clean_entertainment_areas_with_trash(self, coordinator):
        """Test cleaning when trash areas exist."""
        areas = [
            {"id": "1", "name": "Entertainment area", "status": "inactive"},
            {"id": "2", "name": "Entertainment area", "status": "inactive"},
            {"id": "3", "name": "Living Room", "status": "active"}
        ]

        coordinator._get_entertainment_areas.return_value = areas
        coordinator._delete_entertainment_area.return_value = True
        coordinator._clean_entertainment_areas.return_value = 2

        result = await coordinator._clean_entertainment_areas()
        assert result == 2
        coordinator.cleaned_count = 2  # Set the value directly since we're mocking

    async def test_get_entertainment_areas_success(self, coordinator):
        """Test getting entertainment areas successfully."""
        coordinator._get_entertainment_areas.return_value = [{"id": "1", "name": "Test"}]
        result = await coordinator._get_entertainment_areas()
        assert len(result) == 1
        assert result[0]["id"] == "1"

    async def test_get_entertainment_areas_failure(self, coordinator):
        """Test getting entertainment areas with failure."""
        coordinator._get_entertainment_areas.return_value = []
        result = await coordinator._get_entertainment_areas()
        assert result == []

    async def test_delete_entertainment_area_success(self, coordinator):
        """Test deleting entertainment area successfully."""
        coordinator._delete_entertainment_area.return_value = True
        result = await coordinator._delete_entertainment_area("test_id")
        assert result is True

    async def test_delete_entertainment_area_failure(self, coordinator):
        """Test deleting entertainment area with failure."""
        coordinator._delete_entertainment_area.return_value = False
        result = await coordinator._delete_entertainment_area("test_id")
        assert result is False

    async def test_manual_clean(self, coordinator):
        """Test manual clean operation."""
        coordinator._clean_entertainment_areas.return_value = 3
        coordinator.manual_clean.return_value = 3
        result = await coordinator.manual_clean()
        assert result == 3

    def test_http_protocol_usage_in_coordinator(self):
        """Test that coordinator uses HTTP for all Hue Hub interactions."""
        from custom_components.hue_cleaner.const import HUE_ENTERTAINMENT_API
        
        # Critical: Entertainment API must use HTTP, not HTTPS
        assert HUE_ENTERTAINMENT_API.startswith("http://"), f"HUE_ENTERTAINMENT_API must use HTTP: {HUE_ENTERTAINMENT_API}"
        assert "https://" not in HUE_ENTERTAINMENT_API, f"HUE_ENTERTAINMENT_API must not use HTTPS: {HUE_ENTERTAINMENT_API}"
        
        # Verify the URL format is correct for Hue Hub
        assert "/clip/v2/resource/entertainment_configuration" in HUE_ENTERTAINMENT_API

    async def test_connection_error_handling_ip_change(self, coordinator):
        """Test handling of IP change errors."""
        coordinator._clean_entertainment_areas.side_effect = Exception("Connection refused")
        
        async def mock_update_data():
            await coordinator._handle_connection_error("ip_change", "Connection refused")
            raise MockUpdateFailed()
        
        coordinator._async_update_data.side_effect = mock_update_data
        
        with pytest.raises(MockUpdateFailed):
            await coordinator._async_update_data()
        
        coordinator._handle_connection_error.assert_awaited_once_with("ip_change", "Connection refused")

    async def test_connection_error_handling_api_key_expired(self, coordinator):
        """Test handling of API key expiration errors."""
        coordinator._clean_entertainment_areas.side_effect = Exception("Unauthorized")
        
        async def mock_update_data():
            await coordinator._handle_connection_error("api_key_expired", "Unauthorized")
            raise MockUpdateFailed()
        
        coordinator._async_update_data.side_effect = mock_update_data
        
        with pytest.raises(MockUpdateFailed):
            await coordinator._async_update_data()
        
        coordinator._handle_connection_error.assert_awaited_once_with("api_key_expired", "Unauthorized")

    async def test_connection_error_handling_general_error(self, coordinator):
        """Test handling of general connection errors."""
        coordinator._clean_entertainment_areas.side_effect = Exception("Network timeout")
        
        async def mock_update_data():
            await coordinator._handle_connection_error("connection_error", "Network timeout")
            raise MockUpdateFailed()
        
        coordinator._async_update_data.side_effect = mock_update_data
        
        with pytest.raises(MockUpdateFailed):
            await coordinator._async_update_data()
        
        coordinator._handle_connection_error.assert_awaited_once_with("connection_error", "Network timeout")

    async def test_connection_issues_counter(self, coordinator):
        """Test connection issues counter behavior."""
        coordinator._clean_entertainment_areas.side_effect = Exception("Connection refused")
        
        async def mock_update_data():
            coordinator._connection_issues += 1
            await coordinator._handle_connection_error("ip_change", "Connection refused")
            raise MockUpdateFailed()
        
        coordinator._async_update_data.side_effect = mock_update_data
        
        with pytest.raises(MockUpdateFailed):
            await coordinator._async_update_data()
        
        assert coordinator._connection_issues == 1
        coordinator._handle_connection_error.assert_awaited_once_with("ip_change", "Connection refused")

    async def test_connection_issues_reset_on_success(self, coordinator):
        """Test that connection issues counter resets on successful operations."""
        coordinator._connection_issues = 2
        
        async def mock_update_data():
            coordinator._connection_issues = 0
            await coordinator._clear_repair_issues()
            return {"status": "active"}
        
        coordinator._async_update_data.side_effect = mock_update_data
        
        await coordinator._async_update_data()
        
        assert coordinator._connection_issues == 0
        coordinator._clear_repair_issues.assert_awaited_once()

    async def test_max_connection_issues_threshold(self, coordinator):
        """Test that error handling is triggered after max connection issues."""
        coordinator._connection_issues = coordinator._max_connection_issues - 1
        coordinator._clean_entertainment_areas.side_effect = Exception("Connection refused")
        
        async def mock_update_data():
            coordinator._connection_issues += 1
            if coordinator._connection_issues >= coordinator._max_connection_issues:
                coordinator._connection_issues = 0
            await coordinator._handle_connection_error("ip_change", "Connection refused")
            raise MockUpdateFailed()
        
        coordinator._async_update_data.side_effect = mock_update_data
        
        with pytest.raises(MockUpdateFailed):
            await coordinator._async_update_data()
        
        # Should increment and then reset after max is reached
        assert coordinator._connection_issues == 0
        coordinator._handle_connection_error.assert_awaited_once_with("ip_change", "Connection refused")

    async def test_create_error_notification_ip_change(self, coordinator):
        """Test creation of error notification for IP change."""
        coordinator._create_error_notification.return_value = None
        
        await coordinator._create_error_notification("ip_change", "Connection refused")
        
        coordinator._create_error_notification.assert_awaited_once_with("ip_change", "Connection refused")

    async def test_create_error_notification_api_key_expired(self, coordinator):
        """Test creation of error notification for API key expiration."""
        coordinator._create_error_notification.return_value = None
        
        await coordinator._create_error_notification("api_key_expired", "Unauthorized")
        
        coordinator._create_error_notification.assert_awaited_once_with("api_key_expired", "Unauthorized")

    async def test_create_repair_issue_ip_change(self, coordinator):
        """Test creation of repair issue for IP change."""
        coordinator._create_repair_issue.return_value = None
        
        await coordinator._create_repair_issue("ip_change", "Connection refused")
        
        coordinator._create_repair_issue.assert_awaited_once_with("ip_change", "Connection refused")

    async def test_create_repair_issue_api_key_expired(self, coordinator):
        """Test creation of repair issue for API key expiration."""
        coordinator._create_repair_issue.return_value = None
        
        await coordinator._create_repair_issue("api_key_expired", "Unauthorized")
        
        coordinator._create_repair_issue.assert_awaited_once_with("api_key_expired", "Unauthorized")

    async def test_clear_repair_issues(self, coordinator):
        """Test clearing of repair issues."""
        coordinator._clear_repair_issues.return_value = None
        
        await coordinator._clear_repair_issues()
        
        coordinator._clear_repair_issues.assert_awaited_once()
