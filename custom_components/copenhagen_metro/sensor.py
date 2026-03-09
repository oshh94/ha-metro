"""Sensor platform for Copenhagen Metro traffic information."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .entity import CopenhagenMetroEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import (
        CopenhagenMetroDataUpdateCoordinator,
        PlannedMaintenanceCoordinator,
    )
    from .data import CopenhagenMetroConfigEntry


def _strip_html(text: str) -> str:
    """Strip HTML tags and unescape entities from a string."""
    return html.unescape(re.sub(r"<[^>]+>", " ", text)).strip()


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
            if (
                str(setup.get("lineGroup", "")).strip()
                != self.entity_description.line_group
            ):
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
        messages = [
            {
                "message": str(message.get("name", "")).strip(),
                "create_date": message.get("createDate"),
                "is_clear_message": bool(message.get("isClearMessage", False)),
            }
            for message in self._line_messages()
        ]
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


@dataclass(frozen=True, kw_only=True)
class CopenhagenMetroMaintenanceSensorDescription(SensorEntityDescription):
    """Describes a Copenhagen Metro planned maintenance sensor."""

    line: str = ""
    entity_picture: str | None = None


PLANNED_MAINTENANCE_DESCRIPTIONS: tuple[
    CopenhagenMetroMaintenanceSensorDescription, ...
] = (
    CopenhagenMetroMaintenanceSensorDescription(
        key="m1_planned_maintenance",
        name="M1 planned maintenance",
        icon="mdi:wrench-clock",
        line="M1",
        entity_picture="/copenhagen_metro/brand/m1_m2_icon.png",
    ),
    CopenhagenMetroMaintenanceSensorDescription(
        key="m2_planned_maintenance",
        name="M2 planned maintenance",
        icon="mdi:wrench-clock",
        line="M2",
        entity_picture="/copenhagen_metro/brand/m1_m2_icon.png",
    ),
    CopenhagenMetroMaintenanceSensorDescription(
        key="m3_planned_maintenance",
        name="M3 planned maintenance",
        icon="mdi:wrench-clock",
        line="M3",
        entity_picture="/copenhagen_metro/brand/m3_m4_icon.png",
    ),
    CopenhagenMetroMaintenanceSensorDescription(
        key="m4_planned_maintenance",
        name="M4 planned maintenance",
        icon="mdi:wrench-clock",
        line="M4",
        entity_picture="/copenhagen_metro/brand/m3_m4_icon.png",
    ),
)


class PlannedMaintenanceSensor(CopenhagenMetroEntity, SensorEntity):
    """Sensor showing upcoming planned maintenance for a single metro line."""

    entity_description: CopenhagenMetroMaintenanceSensorDescription

    def __init__(
        self,
        coordinator: PlannedMaintenanceCoordinator,
        description: CopenhagenMetroMaintenanceSensorDescription,
    ) -> None:
        """Initialize the planned maintenance sensor."""
        super().__init__(coordinator)  # type: ignore[arg-type]
        self.entity_description = description
        self._attr_unique_id = f"copenhagen_metro_{description.key}"
        self._attr_entity_picture = description.entity_picture

    def _entries(self) -> list[dict[str, Any]]:
        """Return planned maintenance entries for this line."""
        return self.coordinator.data.get(self.entity_description.line, [])  # type: ignore[return-value]

    @property
    def native_value(self) -> int:
        """Return number of planned maintenance entries in the query window."""
        return len(self._entries())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return planned maintenance details."""
        entries = [
            {
                "title": item.get("title", ""),
                "description": _strip_html(item.get("description", "")),
                "start": item.get("startDate"),
                "end": item.get("endDate"),
                "metro_bus": item.get("metroBus", False),
                "affected_lines": item.get("affectedLines", []),
            }
            for item in self._entries()
        ]
        return {"line": self.entity_description.line, "entries": entries}


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: CopenhagenMetroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Copenhagen Metro sensors from a config entry."""
    coordinator = entry.runtime_data.coordinator
    maintenance_coordinator = entry.runtime_data.maintenance_coordinator

    async_add_entities(
        [
            *(
                CopenhagenMetroLineMessageSensor(coordinator, description)
                for description in LINE_SENSOR_DESCRIPTIONS
            ),
            CopenhagenMetroElevatorOutagesSensor(coordinator, ELEVATOR_DESCRIPTION),
            *(
                PlannedMaintenanceSensor(maintenance_coordinator, description)
                for description in PLANNED_MAINTENANCE_DESCRIPTIONS
            ),
        ]
    )
