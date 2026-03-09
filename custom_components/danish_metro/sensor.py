"""Sensor platform for Danish Metro traffic information."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
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


class DanishMetroTrafficMessagesSensor(DanishMetroCoordinatorEntity, SensorEntity):
    """Sensor containing current line traffic messages."""

    _attr_name = "Traffic messages"
    _attr_unique_id = "danish_metro_traffic_messages"
    _attr_icon = "mdi:train"

    @property
    def native_value(self) -> str:
        """Return a short global status text."""
        if self.coordinator.data.get("active_warning", False):
            return "Warnings active"
        return "Running normally"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return all active line messages."""
        messages: list[dict[str, Any]] = []
        for message in self.coordinator.data.get("active_messages", []):
            line_setup = message.get("lineSetup") or {}
            messages.append(
                {
                    "line_group": (line_setup.get("lineGroup") or "Unknown").strip(),
                    "message": str(message.get("name", "")).strip(),
                    "create_date": message.get("createDate"),
                    "is_clear_message": bool(message.get("isClearMessage", False)),
                }
            )
        return {"messages": messages}


class DanishMetroInstallationsSensor(DanishMetroCoordinatorEntity, SensorEntity):
    """Sensor containing current installation outages."""

    _attr_name = "Installation outages"
    _attr_unique_id = "danish_metro_installation_outages"
    _attr_icon = "mdi:elevator"

    @property
    def native_value(self) -> int:
        """Return number of stations with active installation issues."""
        return len(self.coordinator.data.get("installations", []))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return installation outage details."""
        stations: list[dict[str, Any]] = []
        for installation in self.coordinator.data.get("installations", []):
            station_name = str(installation.get("item1", "")).strip()
            messages: list[str] = []
            for item in installation.get("item2", []):
                status = str(item.get("statusMessage", "")).strip()
                if status:
                    messages.append(status)

            stations.append({"station_name": station_name, "messages": messages})

        return {"stations": stations}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danish Metro sensors from a config entry."""
    coordinator: DanishMetroDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            DanishMetroTrafficMessagesSensor(coordinator),
            DanishMetroInstallationsSensor(coordinator),
        ]
    )
