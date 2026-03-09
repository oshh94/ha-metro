"""Custom types for the Danish Metro integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from .coordinator import DanishMetroDataUpdateCoordinator

type DanishMetroConfigEntry = ConfigEntry["DanishMetroData"]


@dataclass
class DanishMetroData:
    """Data stored in config entry runtime_data."""

    coordinator: DanishMetroDataUpdateCoordinator
