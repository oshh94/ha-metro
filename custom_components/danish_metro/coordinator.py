"""DataUpdateCoordinator for Danish Metro operational data."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    DanishMetroApiClient,
    DanishMetroApiClientAuthenticationError,
    DanishMetroApiClientError,
)
from .const import DOMAIN, LOGGER, SCAN_INTERVAL_SECONDS

if TYPE_CHECKING:
    from .data import DanishMetroConfigEntry


class DanishMetroDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Danish Metro API data."""

    config_entry: DanishMetroConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: DanishMetroApiClient,
        config_entry: DanishMetroConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            payload = await self.client.async_get_data()
        except DanishMetroApiClientAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except DanishMetroApiClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        return {
            "active_messages": payload.get("activeMessages", []),
            "installations": payload.get("installations", []),
        }
