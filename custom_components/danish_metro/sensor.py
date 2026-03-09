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


class DanishMetroLineMessageSensor(DanishMetroCoordinatorEntity, SensorEntity):
    """Sensor containing current traffic message for a metro line group."""

    _attr_icon = "mdi:train"

    def __init__(self, coordinator: DanishMetroDataUpdateCoordinator, line_group: str) -> None:
        """Initialize the line message sensor."""
        super().__init__(coordinator)
        self._line_group = line_group
        self._attr_name = f"{line_group} message"
        self._attr_unique_id = f"danish_metro_message_{line_group.lower().replace('/', '_')}"

    def _line_messages(self) -> list[dict[str, Any]]:
        """Return active messages for the configured line group."""
        messages: list[dict[str, Any]] = []
        for message in self.coordinator.data.get("active_messages", []):
            setup = message.get("lineSetup") or {}
            if str(setup.get("lineGroup", "")).strip() != self._line_group:
                continue
            messages.append(message)
        return messages

    @property
    def native_value(self) -> str:
        """Return the current message for this line group."""
        messages = self._line_messages()
        if not messages:
            return "No current message"

        latest_message = str(messages[0].get("name", "")).strip()
        return latest_message or "No current message"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return all active messages for this line group."""
        messages: list[dict[str, Any]] = []
        for message in self._line_messages():
            messages.append(
                {
                    "message": str(message.get("name", "")).strip(),
                    "create_date": message.get("createDate"),
                    "is_clear_message": bool(message.get("isClearMessage", False)),
                }
            )

        return {
            "line_group": self._line_group,
            "message_count": len(messages),
            "messages": messages,
        }


class DanishMetroElevatorOutagesSensor(DanishMetroCoordinatorEntity, SensorEntity):
    """Sensor containing current elevator outages."""

    _attr_name = "Elevator outages"
    _attr_unique_id = "danish_metro_elevator_outages"
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
            DanishMetroLineMessageSensor(coordinator, "M1/M2"),
            DanishMetroLineMessageSensor(coordinator, "M3/M4"),
            DanishMetroElevatorOutagesSensor(coordinator),
        ]
    )
