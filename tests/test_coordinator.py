"""Test coordinator for Hue Cleaner integration."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from custom_components.hue_cleaner.coordinator import HueCleanerCoordinator


class TestHueCleanerCoordinator:
    """Test Hue Cleaner coordinator."""

    @pytest.fixture
    def coordinator(self, mock_hass):
        """Create coordinator instance."""
        return HueCleanerCoordinator(
            mock_hass,
            "192.168.1.100",
            "test_api_key"
        )

    async def test_init(self, coordinator):
        """Test coordinator initialization."""
        assert coordinator.hue_ip == "192.168.1.100"
        assert coordinator.api_key == "test_api_key"
        assert coordinator.cleaned_count == 0
        assert coordinator.last_clean is None

    async def test_clean_entertainment_areas_no_areas(self, coordinator):
        """Test cleaning when no areas exist."""
        with patch.object(coordinator, "_get_entertainment_areas", return_value=[]):
            result = await coordinator._clean_entertainment_areas()
            assert result == 0

    async def test_clean_entertainment_areas_no_trash(self, coordinator):
        """Test cleaning when no trash areas exist."""
        areas = [
            {"id": "1", "name": "Living Room", "status": "active"},
            {"id": "2", "name": "Bedroom", "status": "active"}
        ]
        
        with patch.object(coordinator, "_get_entertainment_areas", return_value=areas):
            result = await coordinator._clean_entertainment_areas()
            assert result == 0

    async def test_clean_entertainment_areas_with_trash(self, coordinator):
        """Test cleaning when trash areas exist."""
        areas = [
            {"id": "1", "name": "Entertainment area", "status": "inactive"},
            {"id": "2", "name": "Entertainment area", "status": "inactive"},
            {"id": "3", "name": "Living Room", "status": "active"}
        ]
        
        with patch.object(coordinator, "_get_entertainment_areas", return_value=areas), \
             patch.object(coordinator, "_delete_entertainment_area", return_value=True):
            
            result = await coordinator._clean_entertainment_areas()
            assert result == 2
            assert coordinator.cleaned_count == 2

    async def test_get_entertainment_areas_success(self, coordinator):
        """Test getting entertainment areas successfully."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": [{"id": "1", "name": "Test"}]})
        
        with patch("aiohttp.ClientSession.get", return_value=mock_response):
            result = await coordinator._get_entertainment_areas()
            assert len(result) == 1
            assert result[0]["id"] == "1"

    async def test_get_entertainment_areas_failure(self, coordinator):
        """Test getting entertainment areas with failure."""
        mock_response = MagicMock()
        mock_response.status = 404
        
        with patch("aiohttp.ClientSession.get", return_value=mock_response):
            result = await coordinator._get_entertainment_areas()
            assert result == []

    async def test_delete_entertainment_area_success(self, coordinator):
        """Test deleting entertainment area successfully."""
        mock_response = MagicMock()
        mock_response.status = 200
        
        with patch("aiohttp.ClientSession.delete", return_value=mock_response):
            result = await coordinator._delete_entertainment_area("test_id")
            assert result is True

    async def test_delete_entertainment_area_failure(self, coordinator):
        """Test deleting entertainment area with failure."""
        mock_response = MagicMock()
        mock_response.status = 404
        
        with patch("aiohttp.ClientSession.delete", return_value=mock_response):
            result = await coordinator._delete_entertainment_area("test_id")
            assert result is False

    async def test_manual_clean(self, coordinator):
        """Test manual clean operation."""
        with patch.object(coordinator, "_clean_entertainment_areas", return_value=3):
            result = await coordinator.manual_clean()
            assert result == 3
