"""Services for Hue Cleaner integration."""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Hue Cleaner."""

    async def clean_now(call: ServiceCall) -> None:
        """Service to manually clean inactive entertainment areas."""
        # Get all coordinators
        for entry_id, coordinator in hass.data[DOMAIN].items():
            if isinstance(entry_id, str):  # Skip non-entry items
                cleaned = await coordinator.async_manual_clean(include_active=False)
                _LOGGER.info(
                    f"Manually cleaned {cleaned} inactive entertainment areas")

    async def clean_all(call: ServiceCall) -> None:
        """Service to clean all entertainment areas including active ones."""
        # Get all coordinators
        for entry_id, coordinator in hass.data[DOMAIN].items():
            if isinstance(entry_id, str):  # Skip non-entry items
                cleaned = await coordinator.async_manual_clean(include_active=True)
                _LOGGER.warning(
                    f"Manually cleaned {cleaned} entertainment areas (including active)")

    # Register services
    hass.services.async_register(DOMAIN, "clean_now", clean_now)
    hass.services.async_register(DOMAIN, "clean_all", clean_all)
