"""Base entity for the Danish Metro integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import DanishMetroDataUpdateCoordinator


class DanishMetroEntity(CoordinatorEntity[DanishMetroDataUpdateCoordinator]):
    """Base class for Danish Metro entities."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: DanishMetroDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
        )
