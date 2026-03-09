"""The Danish Metro integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DanishMetroApiClient
from .coordinator import DanishMetroDataUpdateCoordinator
from .data import DanishMetroConfigEntry, DanishMetroData

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: DanishMetroConfigEntry) -> bool:
    """Set up Danish Metro from a config entry."""
    coordinator = DanishMetroDataUpdateCoordinator(
        hass,
        client=DanishMetroApiClient(session=async_get_clientsession(hass)),
        config_entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = DanishMetroData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: DanishMetroConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant, entry: DanishMetroConfigEntry
) -> None:
    """Reload a config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
