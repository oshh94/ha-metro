"""Binary sensor platform for Danish Metro traffic information."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import DanishMetroDataUpdateCoordinator


class DanishMetroCoordinatorEntity(CoordinatorEntity[DanishMetroDataUpdateCoordinator]):
    """Base entity for Danish Metro entities."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True


class DanishMetroActiveWarningBinarySensor(DanishMetroCoordinatorEntity, BinarySensorEntity):
    """Binary sensor showing whether any active warning is present."""

    _attr_name = "Active warning"
    _attr_unique_id = "danish_metro_active_warning"
    _attr_icon = "mdi:alert"

    @property
    def is_on(self) -> bool:
        """Return true if active warning is present."""
        return bool(self.coordinator.data.get("active_warning", False))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danish Metro binary sensors from a config entry."""
    coordinator: DanishMetroDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DanishMetroActiveWarningBinarySensor(coordinator)])
