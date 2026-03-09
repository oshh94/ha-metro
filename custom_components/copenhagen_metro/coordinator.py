"""DataUpdateCoordinator for Copenhagen Metro operational data."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import (
    CopenhagenMetroApiClient,
    CopenhagenMetroApiClientAuthenticationError,
    CopenhagenMetroApiClientError,
)
from .const import (
    DOMAIN,
    LOGGER,
    PLANNED_MAINTENANCE_DAYS_AHEAD,
    PLANNED_MAINTENANCE_SCAN_INTERVAL_SECONDS,
    SCAN_INTERVAL_SECONDS,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

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
            msg = f"Error communicating with API: {err}"
            raise UpdateFailed(msg) from err

        active_messages = payload.get("activeMessages", [])
        installations = payload.get("installations", [])
        LOGGER.debug(
            "Operational data updated: %d active message(s), "
            "%d station(s) with elevator outages",
            len(active_messages),
            len(installations),
        )
        return {
            "active_messages": active_messages,
            "installations": installations,
        }


class PlannedMaintenanceCoordinator(
    DataUpdateCoordinator[dict[str, list[dict[str, Any]]]]
):
    """Coordinator for planned maintenance data."""

    config_entry: CopenhagenMetroConfigEntry  # type: ignore[assignment]

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
            name=f"{DOMAIN}_planned_maintenance",
            update_interval=timedelta(
                seconds=PLANNED_MAINTENANCE_SCAN_INTERVAL_SECONDS
            ),
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, list[dict[str, Any]]]:
        """Fetch planned maintenance for today and the next N days."""
        culture = "da" if self.hass.config.language == "da" else "en"
        today = dt_util.now().date()
        LOGGER.debug(
            "Fetching planned maintenance for %d days from %s (culture=%s)",
            PLANNED_MAINTENANCE_DAYS_AHEAD,
            today,
            culture,
        )

        all_entries: list[dict[str, Any]] = []
        for i in range(PLANNED_MAINTENANCE_DAYS_AHEAD):
            date_str = (today + timedelta(days=i)).strftime("%Y%m%d")
            try:
                entries = await self.client.async_get_planned_maintenance(
                    date_str, culture
                )
            except CopenhagenMetroApiClientAuthenticationError as err:
                raise ConfigEntryAuthFailed from err
            except CopenhagenMetroApiClientError as err:
                msg = f"Error fetching planned maintenance: {err}"
                raise UpdateFailed(msg) from err
            LOGGER.debug(
                "Planned maintenance for %s: %d entry/entries", date_str, len(entries)
            )
            all_entries.extend(entries)

        by_line: dict[str, list[dict[str, Any]]] = {
            "M1": [],
            "M2": [],
            "M3": [],
            "M4": [],
        }
        for entry in all_entries:
            line = entry.get("lines", "").upper()
            if line in by_line:
                by_line[line].append(entry)

        LOGGER.debug(
            "Planned maintenance updated: %s",
            {line: len(entries) for line, entries in by_line.items()},
        )
        return by_line
