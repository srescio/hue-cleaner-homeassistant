"""Sensor platform for Hue Cleaner integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hue Cleaner sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([HueCleanerSensor(coordinator, config_entry)])


class HueCleanerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Hue Cleaner sensor."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:broom"
        self._attr_translation_key = "status"
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

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "unknown"
        return self.coordinator.data.get("status", "unknown")

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        return {
            "cleaned_count": self.coordinator.data.get("cleaned_count", 0),
            "last_clean": self.coordinator.data.get("last_clean"),
            "areas_cleaned_this_run": self.coordinator.data.get("areas_cleaned_this_run", 0),
            "hue_ip": self.coordinator.data.get("hue_ip"),
            "mode": self.coordinator.data.get("mode", "unknown"),
        }
