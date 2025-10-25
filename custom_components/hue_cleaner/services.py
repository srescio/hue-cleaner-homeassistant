"""Services for Hue Cleaner integration."""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Hue Cleaner."""

    async def clean_entertainment_areas(call: ServiceCall) -> None:
        """Service to manually clean entertainment areas."""
        entity_id = call.data.get("entity_id")
        
        if not entity_id:
            _LOGGER.error("Entity ID is required")
            return

        # Find the coordinator for this entity
        entity_registry = er.async_get(hass)
        entity = entity_registry.async_get(entity_id)
        
        if not entity or entity.platform != DOMAIN:
            _LOGGER.error(f"Entity {entity_id} is not a Hue Cleaner entity")
            return

        # Get the coordinator
        config_entry_id = entity.config_entry_id
        if config_entry_id not in hass.data[DOMAIN]:
            _LOGGER.error("Hue Cleaner coordinator not found")
            return

        coordinator = hass.data[DOMAIN][config_entry_id]
        
        # Trigger manual clean
        cleaned = await coordinator.manual_clean()
        _LOGGER.info(f"Manually cleaned {cleaned} entertainment areas")

    # Register the service
    hass.services.async_register(
        DOMAIN,
        "clean_entertainment_areas",
        clean_entertainment_areas,
    )
