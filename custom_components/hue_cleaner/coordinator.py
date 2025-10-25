"""Data coordinator for Hue Cleaner integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_SCAN_INTERVAL,
    HUE_ENTERTAINMENT_API,
    ENTERTAINMENT_AREA_NAME_PATTERN,
    ENTERTAINMENT_AREA_INACTIVE_STATUS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class HueCleanerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Hue Hub."""

    def __init__(self, hass: HomeAssistant, hue_ip: str, api_key: str) -> None:
        """Initialize."""
        self.hue_ip = hue_ip
        self.api_key = api_key
        self.cleaned_count = 0
        self.last_clean = None

        super().__init__(
            hass,
            _LOGGER,
            name="Hue Cleaner",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # Clean entertainment areas
            cleaned = await self._clean_entertainment_areas()
            
            return {
                "cleaned_count": self.cleaned_count,
                "last_clean": self.last_clean,
                "areas_cleaned_this_run": cleaned,
                "hue_ip": self.hue_ip,
                "status": "active" if cleaned >= 0 else "error",
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Hue Hub: {err}")

    async def _clean_entertainment_areas(self) -> int:
        """Clean up inactive entertainment areas."""
        try:
            # Get entertainment areas
            areas = await self._get_entertainment_areas()
            if not areas:
                return 0

            # Filter inactive areas with the pattern
            trash_areas = [
                area
                for area in areas
                if (
                    area.get("name", "").startswith(ENTERTAINMENT_AREA_NAME_PATTERN)
                    and area.get("status") == ENTERTAINMENT_AREA_INACTIVE_STATUS
                )
            ]

            if not trash_areas:
                return 0

            # Delete each area
            cleaned = 0
            for area in trash_areas:
                if await self._delete_entertainment_area(area["id"]):
                    cleaned += 1
                    # Small delay to avoid overwhelming the hub
                    await asyncio.sleep(0.5)

            # Update counters
            self.cleaned_count += cleaned
            self.last_clean = datetime.now()

            _LOGGER.info(f"Cleaned {cleaned} entertainment areas")
            return cleaned

        except Exception as err:
            _LOGGER.error(f"Error cleaning entertainment areas: {err}")
            return -1

    async def _get_entertainment_areas(self) -> list[dict]:
        """Get all entertainment areas from Hue Hub."""
        try:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                connector=aiohttp.TCPConnector(ssl=False)
            )
            
            url = HUE_ENTERTAINMENT_API.format(ip=self.hue_ip)
            headers = {"hue-application-key": self.api_key}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    _LOGGER.error(f"Failed to get entertainment areas: {response.status}")
                    return []
        except Exception as err:
            _LOGGER.error(f"Error getting entertainment areas: {err}")
            return []
        finally:
            await session.close()

    async def _delete_entertainment_area(self, area_id: str) -> bool:
        """Delete a specific entertainment area."""
        try:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                connector=aiohttp.TCPConnector(ssl=False)
            )
            
            url = f"{HUE_ENTERTAINMENT_API.format(ip=self.hue_ip)}/{area_id}"
            headers = {"hue-application-key": self.api_key}
            
            async with session.delete(url, headers=headers) as response:
                success = response.status in [200, 204]
                if success:
                    _LOGGER.debug(f"Deleted entertainment area {area_id}")
                else:
                    _LOGGER.warning(f"Failed to delete area {area_id}: {response.status}")
                return success
        except Exception as err:
            _LOGGER.error(f"Error deleting entertainment area {area_id}: {err}")
            return False
        finally:
            await session.close()

    async def manual_clean(self) -> int:
        """Manually trigger a clean operation."""
        return await self._clean_entertainment_areas()
