"""Custom types for the Copenhagen Metro integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from .coordinator import (
        CopenhagenMetroDataUpdateCoordinator,
        PlannedMaintenanceCoordinator,
    )

type CopenhagenMetroConfigEntry = ConfigEntry["CopenhagenMetroData"]


@dataclass
class CopenhagenMetroData:
    """Data stored in config entry runtime_data."""

    coordinator: CopenhagenMetroDataUpdateCoordinator
    maintenance_coordinator: PlannedMaintenanceCoordinator
