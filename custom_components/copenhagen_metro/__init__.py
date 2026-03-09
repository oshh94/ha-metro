"""The Copenhagen Metro integration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from .api import CopenhagenMetroApiClient
from .const import LOGGER
from .coordinator import (
    CopenhagenMetroDataUpdateCoordinator,
    PlannedMaintenanceCoordinator,
)
from .data import CopenhagenMetroConfigEntry, CopenhagenMetroData

PLATFORMS: list[Platform] = [Platform.SENSOR]

_BRAND_URL = "/copenhagen_metro/brand"


async def async_setup(hass: HomeAssistant, _config: dict) -> bool:
    """Register static path for brand images once per HA session."""
    LOGGER.debug("Registering static path %s", _BRAND_URL)
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                _BRAND_URL, str(Path(__file__).parent / "brand"), cache_headers=True
            )
        ]
    )
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: CopenhagenMetroConfigEntry
) -> bool:
    """Set up Copenhagen Metro from a config entry."""
    LOGGER.debug("Setting up entry %s", entry.entry_id)
    client = CopenhagenMetroApiClient(session=async_get_clientsession(hass))

    coordinator = CopenhagenMetroDataUpdateCoordinator(
        hass,
        client=client,
        config_entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()
    LOGGER.debug("Operational data coordinator ready")

    maintenance_coordinator = PlannedMaintenanceCoordinator(
        hass,
        client=client,
        config_entry=entry,
    )
    await maintenance_coordinator.async_config_entry_first_refresh()
    LOGGER.debug("Planned maintenance coordinator ready")

    entry.runtime_data = CopenhagenMetroData(
        coordinator=coordinator,
        maintenance_coordinator=maintenance_coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    LOGGER.debug("Entry %s set up successfully", entry.entry_id)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: CopenhagenMetroConfigEntry
) -> bool:
    """Unload a config entry."""
    LOGGER.debug("Unloading entry %s", entry.entry_id)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant, entry: CopenhagenMetroConfigEntry
) -> None:
    """Reload a config entry."""
    LOGGER.debug("Reloading entry %s", entry.entry_id)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
