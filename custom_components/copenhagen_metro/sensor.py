"""Sensor platform for Copenhagen Metro traffic information."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import CopenhagenMetroDataUpdateCoordinator
from .data import CopenhagenMetroConfigEntry
from .entity import CopenhagenMetroEntity


@dataclass(frozen=True, kw_only=True)
class CopenhagenMetroLineSensorDescription(SensorEntityDescription):
    """Describes a Copenhagen Metro line message sensor."""

    line_group: str = ""
    entity_picture: str | None = None


LINE_SENSOR_DESCRIPTIONS: tuple[CopenhagenMetroLineSensorDescription, ...] = (
    CopenhagenMetroLineSensorDescription(
        key="m1_m2_message",
        name="M1/M2 message",
        icon="mdi:train",
        line_group="M1/M2",
        entity_picture="/copenhagen_metro/brand/m1_m2_icon.png",
    ),
    CopenhagenMetroLineSensorDescription(
        key="m3_m4_message",
        name="M3/M4 message",
        icon="mdi:subway-variant",
        line_group="M3/M4",
        entity_picture="/copenhagen_metro/brand/m3_m4_icon.png",
    ),
)

ELEVATOR_DESCRIPTION = SensorEntityDescription(
    key="elevator_outages",
    name="Elevator outages",
    icon="mdi:elevator",
)


class CopenhagenMetroLineMessageSensor(CopenhagenMetroEntity, SensorEntity):
    """Sensor containing current traffic message for a metro line group."""

    entity_description: CopenhagenMetroLineSensorDescription

    def __init__(
        self,
        coordinator: CopenhagenMetroDataUpdateCoordinator,
        description: CopenhagenMetroLineSensorDescription,
    ) -> None:
        """Initialize the line message sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"copenhagen_metro_{description.key}"
        self._attr_entity_picture = description.entity_picture

    def _line_messages(self) -> list[dict[str, Any]]:
        """Return active messages for the configured line group."""
        messages: list[dict[str, Any]] = []
        for message in self.coordinator.data.get("active_messages", []):
            setup = message.get("lineSetup") or {}
            if str(setup.get("lineGroup", "")).strip() != self.entity_description.line_group:
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
            "line_group": self.entity_description.line_group,
            "message_count": len(messages),
            "messages": messages,
        }


class CopenhagenMetroElevatorOutagesSensor(CopenhagenMetroEntity, SensorEntity):
    """Sensor containing current elevator outages."""

    def __init__(
        self,
        coordinator: CopenhagenMetroDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the elevator outages sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"copenhagen_metro_{description.key}"

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
    entry: CopenhagenMetroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Copenhagen Metro sensors from a config entry."""
    coordinator: CopenhagenMetroDataUpdateCoordinator = entry.runtime_data.coordinator

    async_add_entities(
        [
            *(
                CopenhagenMetroLineMessageSensor(coordinator, description)
                for description in LINE_SENSOR_DESCRIPTIONS
            ),
            CopenhagenMetroElevatorOutagesSensor(coordinator, ELEVATOR_DESCRIPTION),
        ]
    )
