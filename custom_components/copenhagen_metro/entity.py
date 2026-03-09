"""Base entity for the Copenhagen Metro integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import CopenhagenMetroDataUpdateCoordinator


class CopenhagenMetroEntity(CoordinatorEntity[CopenhagenMetroDataUpdateCoordinator]):
    """Base class for Copenhagen Metro entities."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: CopenhagenMetroDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Copenhagen Metro",
            manufacturer="Metroselskabet",
            entry_type=DeviceEntryType.SERVICE,
        )
