"""Data coordinator for Hue Cleaner integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers import issue_registry
from homeassistant.components import persistent_notification

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_CLEANUP_DELAY,
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
        self.hass = hass
        self.hue_ip = hue_ip
        self.api_key = api_key
        self.cleaned_count = 0
        self.last_clean = None
        self._entertainment_area_entities = []
        self._unsubscribe_trackers = []
        self._connection_issues = 0
        self._max_connection_issues = 3

        super().__init__(
            hass,
            _LOGGER,
            name="Hue Cleaner",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def async_start(self) -> None:
        """Start listening to entertainment area entities."""
        await self._setup_entertainment_area_tracking()

    async def _setup_entertainment_area_tracking(self) -> None:
        """Set up tracking of entertainment area entities."""
        # Find all entertainment area entities
        entertainment_entities = [
            entity_id for entity_id in self.hass.states.async_entity_ids("binary_sensor")
            if entity_id.startswith("binary_sensor.entertainment_area_")
        ]
        
        self._entertainment_area_entities = entertainment_entities
        
        if not entertainment_entities:
            _LOGGER.warning("No entertainment area entities found. Philips Hue integration not configured - using polling fallback.")
            _LOGGER.info("Consider setting up Philips Hue integration for more efficient operation.")
            return

        _LOGGER.info(f"Tracking {len(entertainment_entities)} entertainment area entities - using event-driven cleanup")
        
        # Track state changes for all entertainment area entities
        for entity_id in entertainment_entities:
            unsubscribe = async_track_state_change(
                self.hass,
                entity_id,
                self._on_entertainment_area_change
            )
            self._unsubscribe_trackers.append(unsubscribe)

    def _on_entertainment_area_change(self, entity_id, old_state, new_state):
        """Handle entertainment area state changes."""
        if new_state is None:
            return
            
        _LOGGER.debug(f"Entertainment area {entity_id} changed: {old_state.state if old_state else 'None'} -> {new_state.state}")
        
        # If a new entertainment area is created, trigger cleanup after a delay
        if old_state is None and new_state.state == "on":
            _LOGGER.info(f"New entertainment area detected: {entity_id}")
            # Schedule cleanup after a short delay to allow the area to be fully created
            self.hass.async_create_task(self._delayed_cleanup())

    async def _delayed_cleanup(self) -> None:
        """Perform cleanup after a delay."""
        await asyncio.sleep(DEFAULT_CLEANUP_DELAY)  # Wait for the area to be fully created
        await self._clean_entertainment_areas()

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # Check if we're using event-driven or polling mode
            mode = "event-driven" if self._entertainment_area_entities else "polling"
            _LOGGER.debug(f"Running cleanup in {mode} mode")
            
            # Clean entertainment areas
            cleaned = await self._clean_entertainment_areas()
            
            # Reset connection issues on successful operation
            if cleaned >= 0:
                self._connection_issues = 0
                await self._clear_repair_issues()
            
            return {
                "cleaned_count": self.cleaned_count,
                "last_clean": self.last_clean,
                "areas_cleaned_this_run": cleaned,
                "hue_ip": self.hue_ip,
                "status": "active" if cleaned >= 0 else "error",
                "mode": mode,
            }
        except Exception as err:
            # Handle specific error types
            error_message = str(err)
            if "Connection refused" in error_message or "No route to host" in error_message:
                await self._handle_connection_error("ip_change", error_message)
            elif "Unauthorized" in error_message or "401" in error_message:
                await self._handle_connection_error("api_key_expired", error_message)
            else:
                await self._handle_connection_error("connection_error", error_message)
            
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
            raise

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

    async def async_shutdown(self) -> None:
        """Clean up trackers when coordinator is shut down."""
        for unsubscribe in self._unsubscribe_trackers:
            unsubscribe()
        self._unsubscribe_trackers.clear()

    async def _handle_connection_error(self, error_type: str, error_message: str) -> None:
        """Handle connection errors and create notifications/issues."""
        self._connection_issues += 1
        
        if self._connection_issues >= self._max_connection_issues:
            # Create persistent notification
            await self._create_error_notification(error_type, error_message)
            
            # Create repair issue
            await self._create_repair_issue(error_type, error_message)
            
            # Reset counter to avoid spam
            self._connection_issues = 0

    async def _create_error_notification(self, error_type: str, error_message: str) -> None:
        """Create a persistent notification for connection errors."""
        if error_type == "ip_change":
            title = "Hue Cleaner: Hub IP Changed"
            message = f"The Hue Hub IP address has changed. Please reconfigure the integration.\n\nOriginal IP: {self.hue_ip}\nError: {error_message}"
        elif error_type == "api_key_expired":
            title = "Hue Cleaner: API Key Expired"
            message = f"The Hue Hub API key has expired. Please reconfigure the integration.\n\nError: {error_message}"
        else:
            title = "Hue Cleaner: Connection Error"
            message = f"Unable to connect to Hue Hub.\n\nError: {error_message}"
        
        await persistent_notification.async_create(
            self.hass,
            message,
            title=title,
            notification_id=f"hue_cleaner_{error_type}_{self.hue_ip}"
        )

    async def _create_repair_issue(self, error_type: str, error_message: str) -> None:
        """Create a repair issue in the settings."""
        issue_registry_instance = issue_registry.async_get(self.hass)
        
        if error_type == "ip_change":
            issue_id = f"hue_cleaner_ip_change_{self.hue_ip}"
            issue_title = "Hue Cleaner: Hub IP Changed"
            issue_description = f"The Hue Hub IP address has changed from {self.hue_ip}. Please reconfigure the integration."
        elif error_type == "api_key_expired":
            issue_id = f"hue_cleaner_api_key_expired_{self.hue_ip}"
            issue_title = "Hue Cleaner: API Key Expired"
            issue_description = f"The Hue Hub API key has expired. Please reconfigure the integration."
        else:
            issue_id = f"hue_cleaner_connection_error_{self.hue_ip}"
            issue_title = "Hue Cleaner: Connection Error"
            issue_description = f"Unable to connect to Hue Hub: {error_message}"
        
        issue_registry_instance.async_create_issue(
            domain=DOMAIN,
            issue_id=issue_id,
            is_fixable=True,
            is_persistent=True,
            severity=issue_registry.IssueSeverity.ERROR,
            translation_key=error_type,
            translation_placeholders={
                "hue_ip": self.hue_ip,
                "error_message": error_message
            }
        )

    async def _clear_repair_issues(self) -> None:
        """Clear all repair issues for this integration."""
        issue_registry_instance = issue_registry.async_get(self.hass)
        
        # Clear all issues related to this integration
        for issue_id in list(issue_registry_instance.issues.keys()):
            if issue_id.startswith(f"hue_cleaner_{self.hue_ip}"):
                issue_registry_instance.async_delete(domain=DOMAIN, issue_id=issue_id)
