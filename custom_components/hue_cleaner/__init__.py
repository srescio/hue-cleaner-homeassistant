"""Hue Cleaner integration for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HueCleanerCoordinator
from . import services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hue Cleaner from a config entry."""
    try:
        _LOGGER.debug(f"Starting setup for entry {entry.entry_id}")
        hass.data.setdefault(DOMAIN, {})
        
        # Create coordinator
        coordinator = HueCleanerCoordinator(
            hass, 
            entry.data["host"], 
            entry.data["api_key"]
        )
        
        # Fetch initial data
        _LOGGER.debug("Fetching initial data")
        await coordinator.async_config_entry_first_refresh()
        
        # Start tracking entertainment area entities
        _LOGGER.debug("Starting coordinator")
        await coordinator.async_start()
        
        hass.data[DOMAIN][entry.entry_id] = coordinator

        # Forward the setup to the sensor platform.
        _LOGGER.debug(f"Setting up platforms: {PLATFORMS}")
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Set up services
        _LOGGER.debug("Setting up services")
        await services.async_setup_services(hass)
        
        _LOGGER.info("Hue Cleaner setup completed successfully")
        return True
    except Exception as err:
        _LOGGER.error(f"Error setting up Hue Cleaner: {err}", exc_info=True)
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_entry_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        if coordinator:
            await coordinator.async_shutdown()

    return unload_ok
