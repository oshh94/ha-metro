"""DataUpdateCoordinator for Danish Metro operational data."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class DanishMetroDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Danish Metro API data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            response = await self._session.get(API_URL, timeout=15)
            response.raise_for_status()
            payload: dict[str, Any] = await response.json()
        except Exception as err:  # broad by design to surface update failures in HA
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        return {
            "active_messages": payload.get("activeMessages", []),
            "installations": payload.get("installations", []),
        }
