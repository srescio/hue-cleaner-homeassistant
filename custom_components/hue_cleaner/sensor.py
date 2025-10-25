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

    async_add_entities([HueCleanerSensor(coordinator)])


class HueCleanerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Hue Cleaner sensor."""

    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Hue Cleaner"
        self._attr_unique_id = "hue_cleaner_status"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self.coordinator.data.get("status", "unknown")

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            "cleaned_count": self.coordinator.data.get("cleaned_count", 0),
            "last_clean": self.coordinator.data.get("last_clean"),
            "areas_cleaned_this_run": self.coordinator.data.get("areas_cleaned_this_run", 0),
            "hue_ip": self.coordinator.data.get("hue_ip"),
        }
