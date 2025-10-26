"""Button platform for Hue Cleaner integration."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HueCleanerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button platform."""
    coordinator: HueCleanerCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        HueCleanerCleanButton(coordinator, entry),
        HueCleanerCleanAllButton(coordinator, entry),
    ])


class HueCleanerCleanButton(CoordinatorEntity, ButtonEntity):
    """Button to clean inactive entertainment areas."""

    def __init__(self, coordinator: HueCleanerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_clean_button"
        self._attr_icon = "mdi:broom"
        self._attr_has_entity_name = True
        self._attr_translation_key = "clean_inactive"
        self._entry = entry

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"Hue Cleaner ({self.coordinator.hue_ip})",
            "manufacturer": "Custom",
            "model": "Hue Cleaner",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_manual_clean(include_active=False)


class HueCleanerCleanAllButton(CoordinatorEntity, ButtonEntity):
    """Button to clean all entertainment areas including active ones."""

    def __init__(self, coordinator: HueCleanerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_clean_all_button"
        self._attr_icon = "mdi:delete-sweep"
        self._attr_has_entity_name = True
        self._attr_translation_key = "clean_all"
        self._entry = entry

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"Hue Cleaner ({self.coordinator.hue_ip})",
            "manufacturer": "Custom",
            "model": "Hue Cleaner",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_manual_clean(include_active=True)
