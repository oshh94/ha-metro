"""The Copenhagen Metro integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CopenhagenMetroApiClient
from .coordinator import CopenhagenMetroDataUpdateCoordinator
from .data import CopenhagenMetroConfigEntry, CopenhagenMetroData

PLATFORMS: list[Platform] = [Platform.SENSOR]

_BRAND_URL = "/copenhagen_metro/brand"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register static path for brand images once per HA session."""
    hass.http.register_static_path(
        _BRAND_URL,
        str(Path(__file__).parent / "brand"),
        cache_headers=True,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: CopenhagenMetroConfigEntry) -> bool:
    """Set up Copenhagen Metro from a config entry."""
    coordinator = CopenhagenMetroDataUpdateCoordinator(
        hass,
        client=CopenhagenMetroApiClient(session=async_get_clientsession(hass)),
        config_entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = CopenhagenMetroData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: CopenhagenMetroConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant, entry: CopenhagenMetroConfigEntry
) -> None:
    """Reload a config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
