"""DataUpdateCoordinator for Copenhagen Metro operational data."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    CopenhagenMetroApiClient,
    CopenhagenMetroApiClientAuthenticationError,
    CopenhagenMetroApiClientError,
)
from .const import DOMAIN, LOGGER, SCAN_INTERVAL_SECONDS

if TYPE_CHECKING:
    from .data import CopenhagenMetroConfigEntry


class CopenhagenMetroDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Copenhagen Metro API data."""

    config_entry: CopenhagenMetroConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: CopenhagenMetroApiClient,
        config_entry: CopenhagenMetroConfigEntry,
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
        except CopenhagenMetroApiClientAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except CopenhagenMetroApiClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        return {
            "active_messages": payload.get("activeMessages", []),
            "installations": payload.get("installations", []),
        }
